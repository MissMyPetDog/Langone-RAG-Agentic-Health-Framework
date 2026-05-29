"""Orchestrator: plan-act loop integrating SQL agent, patient vector DB,
discharge notes (Chroma), and literature RAG. Final recommendation is
delegated to the partner's `_call_llm`.
"""
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# sql_agent
SQL_AGENT_PARENT = Path("/gpfs/data/razavianlab/capstone/2025_agentic")
if str(SQL_AGENT_PARENT) not in sys.path:
    sys.path.insert(0, str(SQL_AGENT_PARENT))

# retrieve_ehr (patient vector DB)
RETRIEVE_EHR_PATH = Path("/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/orchestrator")
if str(RETRIEVE_EHR_PATH) not in sys.path:
    sys.path.insert(0, str(RETRIEVE_EHR_PATH))

from sql_agent import SQLAgent
from sql_agent import llm as llm_mod

from .lit_retrieval import retrieve_literature
from .lit_generate import generate_recommendation
from .prompts import PLAN_SYSTEM, SUMMARIZE_PATIENT

# discharge notes (Chroma)
import chromadb
from chromadb.utils import embedding_functions


PATIENT_DB_ROOT = Path(
    "/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/patient_db"
)
RUNS_DIR = Path(__file__).parent / "runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)

# --- Rendering limits (tune freely) ---
PLANNER_SQL_ROWS = 100      # how many SQL rows the planner sees per patient_query
PLANNER_VEC_CHARS = 500     # truncate each vector hit text for planner
PLANNER_LIT_CHARS = 800     # truncate each literature passage for planner
PLANNER_NOTES_CHARS = 600   # truncate each discharge-notes chunk for planner
FULL_VEC_CHARS = 500        # vector hit text in full transcript (summarizer/recommender)
FULL_LIT_CHARS = 1600       # literature passage text in full transcript
FULL_NOTES_CHARS = 1200     # discharge-notes chunk text in full transcript

# --- Discharge notes vector DB (Chroma, shared across Orchestrator instances) ---
NOTES_DB_PATH = "/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/NotesDB/ckd_8_db"
NOTES_COLLECTION_NAME = "ckd_8_notes_bge"
K_NOTES = 5

_notes_collection = None  # module-level singleton; BGE-m3 loads once per process


def _get_notes_collection():
    """Lazy singleton. BGE-m3 encoder loads ONCE per process and is shared
    across all Orchestrator instances (important for `--all` runs)."""
    global _notes_collection
    if _notes_collection is None:
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"
        print(f"[orchestrator] Loading discharge notes collection "
              f"(one-time, device={device})...")
        client = chromadb.PersistentClient(path=NOTES_DB_PATH)
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-m3", device=device
        )
        _notes_collection = client.get_collection(
            name=NOTES_COLLECTION_NAME, embedding_function=ef
        )
        print(f"[orchestrator] Notes collection ready: "
              f"{_notes_collection.count()} chunks")
    return _notes_collection


class Orchestrator:
    def __init__(
        self,
        subject_id,
        t_cutoff,
        stage=None,
        max_turns=8,
        k_patient_vector=5,
        k_literature=5,
        k_notes=K_NOTES,
        patient_db_root=PATIENT_DB_ROOT,
    ):
        self.subject_id = str(subject_id)
        self.t_cutoff = str(t_cutoff)
        self.stage = stage
        self.max_turns = max_turns
        self.k_patient_vector = k_patient_vector
        self.k_literature = k_literature
        self.k_notes = k_notes

        self.sql_agent = SQLAgent()
        self.llm_client = llm_mod.get_client()
        self.vector_store = self._load_vector_store(patient_db_root)
        self.notes_collection = _get_notes_collection()
        self.transcript = []

    # ------------------------------------------------------------------
    def run(self, save=True):
        t_start = time.time()
        final_thought = ""

        for turn in range(self.max_turns):
            try:
                action = self._plan(turn)
            except Exception as e:
                print(f"  [planner failed: {e}] forcing finalize")
                final_thought = f"(planner failed: {e})"
                break

            print(f"\n[turn {turn+1}/{self.max_turns}] action={action.get('action')} "
                  f"query={action.get('query','')[:80]!r}")
            print(f"  thought: {action.get('thought','')[:200]}")

            thought = action.get("thought", "")

            if action.get("action") == "finalize":
                final_thought = thought
                break
            if action.get("action") == "query_patient":
                self._do_patient_query(turn, action.get("query", ""), thought)
            elif action.get("action") == "query_literature":
                self._do_literature_query(turn, action.get("query", ""), thought)
            else:
                print(f"  [unknown action {action.get('action')!r}, forcing finalize]")
                final_thought = thought
                break
        else:
            # loop hit max_turns without finalize
            final_thought = "(max_turns reached without finalize)"

        # 2-step finalization
        try:
            patient_summary = self._summarize_patient()
        except Exception as e:
            patient_summary = f"ERROR summarizing patient: {e}"

        try:
            recommendation = self._generate_recommendation(patient_summary)
        except Exception as e:
            recommendation = f"ERROR generating recommendation: {e}"

        result = {
            "subject_id": self.subject_id,
            "t_cutoff": self.t_cutoff,
            "stage": self.stage,
            "started_at": datetime.utcnow().isoformat() + "Z",
            "duration_sec": round(time.time() - t_start, 1),
            "n_turns_used": len(self.transcript),
            "final_thought": final_thought,
            "transcript": self.transcript,
            "patient_summary": patient_summary,
            "recommendation": recommendation,
        }
        if save:
            self._save(result)
        return result

    # ------------------------------------------------------------------
    # Action handlers
    # ------------------------------------------------------------------
    def _do_patient_query(self, turn, query, thought=""):
        # Path 1: SQL agent
        try:
            sql_r = self.sql_agent.ask(
                query, subject_id=self.subject_id, time_cutoff=self.t_cutoff
            )
            sql_record = {
                "sql": sql_r["sql"],
                "n_rows": sql_r["n_rows"],
                "rows_preview": sql_r["rows"][:PLANNER_SQL_ROWS],
                "duration_ms": sql_r["duration_ms"],
                "attempts": sql_r["attempts"],
            }
        except Exception as e:
            sql_record = {"error": str(e)[:2000]}

        # Path 2: patient vector DB
        try:
            hits = self._vector_search(query, k=self.k_patient_vector)
            # hits is list of (metadata_dict, scores_dict)
            vec_record = [
                {
                    "source_table": meta.get("source_table"),
                    "score": float(scores.get("cosine", 0)),
                    "timestamp": meta.get("timestamp"),
                    "text": (meta.get("text") or "")[:400],
                }
                for (meta, scores) in hits
            ]
        except Exception as e:
            vec_record = {"error": str(e)[:2000]}

        # Path 3: discharge notes (Chroma, filtered to this patient only)
        try:
            nres = self.notes_collection.query(
                query_texts=[query],
                n_results=self.k_notes,
                where={"subject_id": self.subject_id},
                include=["documents", "metadatas", "distances"],
            )
            notes_record = []
            if nres.get("ids") and nres["ids"][0]:
                for doc, meta, dist in zip(
                    nres["documents"][0], nres["metadatas"][0], nres["distances"][0]
                ):
                    notes_record.append({
                        "section_name": meta.get("section_name", ""),
                        "hadm_id":      meta.get("hadm_id", ""),
                        "charttime":    meta.get("charttime", ""),
                        "distance":     float(dist),
                        "text":         doc,
                    })
        except Exception as e:
            notes_record = {"error": str(e)[:2000]}

        self.transcript.append({
            "turn": turn,
            "type": "patient_query",
            "thought": thought,
            "query": query,
            "sql_agent": sql_record,
            "vector_db": vec_record,
            "notes": notes_record,
        })

    def _do_literature_query(self, turn, query, thought=""):
        try:
            hits = retrieve_literature(query, topk=self.k_literature)
        except Exception as e:
            hits = [{"error": str(e)[:2000]}]
        self.transcript.append({
            "turn": turn,
            "type": "literature_query",
            "thought": thought,
            "query": query,
            "literature": hits,
        })

    # ------------------------------------------------------------------
    # Planning (our LLM picks next action)
    # ------------------------------------------------------------------
    def _plan(self, turn):
        user_msg = (
            f"subject_id: {self.subject_id}\n"
            f"t_cutoff: {self.t_cutoff}\n"
            f"stage: {self.stage}\n"
            f"turn: {turn + 1} / {self.max_turns}\n\n"
            f"Transcript so far:\n{self._render_transcript_for_planner()}\n\n"
            "Decide the next action. Return JSON only."
        )
        raw = llm_mod.chat(self.llm_client, PLAN_SYSTEM, user_msg)
        return _extract_json(raw)

    # ------------------------------------------------------------------
    # Step 1 of finalization: structured patient summary (our LLM)
    # ------------------------------------------------------------------
    def _summarize_patient(self):
        user_msg = (
            f"Stage: {self.stage}\n"
            f"subject_id: {self.subject_id}\n\n"
            f"Transcript:\n{self._render_full_transcript()}\n\n"
            "Produce the patient context summary now."
        )
        return llm_mod.chat(self.llm_client, SUMMARIZE_PATIENT, user_msg).strip()

    # ------------------------------------------------------------------
    # Step 2 of finalization: partner's LLM produces the recommendation
    # ------------------------------------------------------------------
    def _generate_recommendation(self, patient_summary):
        # Pull all literature blocks we collected during the loop
        lit_blocks = []
        for entry in self.transcript:
            if entry.get("type") == "literature_query":
                for h in entry.get("literature", []):
                    if isinstance(h, dict) and "parent_block_id" in h:
                        lit_blocks.append(h)

        if not lit_blocks:
            return ("ERROR: no literature was retrieved during the loop, "
                    "cannot produce literature-grounded recommendation.")

        # Build the question for partner's _call_llm.
        # Their prompt requires patient context to be IN the question.
        question = (
            f"{patient_summary}\n\n"
            f"---\n\n"
            f"Clinical question: For this patient (CKD {self.stage}), provide three treatment "
            f"options ordered by preference (drugs, procedures, prescriptions), with patient-grounded "
            f"rationale and citations as instructed in the system prompt."
        )

        return generate_recommendation(question, lit_blocks)

    # ------------------------------------------------------------------
    # Transcript rendering
    # ------------------------------------------------------------------
    def _render_transcript_for_planner(self):
        """What the planner sees each turn. Shows ACTUAL retrieved content
        (SQL rows, vector text, discharge-note chunks, literature passages)
        so it can make data-driven decisions and close the loop."""
        if not self.transcript:
            return "(empty)"
        out = []
        for entry in self.transcript:
            tnum = entry["turn"] + 1
            if entry["type"] == "patient_query":
                out.append(f"[T{tnum}] patient_query: {entry['query']!r}")

                # --- SQL agent results ---
                sql = entry["sql_agent"]
                if isinstance(sql, dict) and "error" in sql:
                    out.append(f"  SQL: ERROR {sql['error'][:300]}")
                else:
                    rows = sql.get("rows_preview", [])
                    out.append(f"  SQL ({sql.get('n_rows', 0)} rows):")
                    for r in rows[:PLANNER_SQL_ROWS]:
                        out.append(f"    {r}")
                    if not rows:
                        out.append("    (no rows)")

                # --- Vector DB results ---
                vec = entry["vector_db"]
                if isinstance(vec, list):
                    out.append(f"  VECTOR ({len(vec)} hits):")
                    for h in vec:
                        txt = (h.get("text") or "")[:PLANNER_VEC_CHARS]
                        out.append(
                            f"    [{h.get('source_table')}|cos={h.get('score',0):.3f}"
                            f"|ts={h.get('timestamp','')}] {txt}"
                        )
                else:
                    out.append(f"  VECTOR: error")

                # --- Discharge notes results ---
                notes = entry.get("notes")
                if notes is None:
                    pass  # older transcripts may not have this field
                elif isinstance(notes, dict) and "error" in notes:
                    out.append(f"  NOTES: ERROR {notes['error'][:300]}")
                elif isinstance(notes, list):
                    if not notes:
                        out.append("  NOTES: (no hits)")
                    else:
                        out.append(f"  NOTES ({len(notes)} hits):")
                        for h in notes:
                            sec = (h.get("section_name") or "?")[:35]
                            out.append(
                                f"    [{sec}|hadm={h.get('hadm_id','?')}"
                                f"|d={h.get('distance',0):.3f}] "
                                f"{(h.get('text') or '')[:PLANNER_NOTES_CHARS]}"
                            )

            elif entry["type"] == "literature_query":
                out.append(f"[T{tnum}] literature_query: {entry['query']!r}")
                hits = entry["literature"]
                if isinstance(hits, list):
                    for h in hits:
                        if "error" in h:
                            out.append(f"  LIT ERROR: {h['error'][:300]}")
                        else:
                            title = h.get("title") or "?"
                            out.append(
                                f"  [{h['parent_block_id']}|{title[:80]}|cos={h.get('score',0):.3f}]"
                            )
                            out.append(f"    {h['text'][:PLANNER_LIT_CHARS]}")
                else:
                    out.append("  LIT: error")
            out.append("")
        return "\n".join(out)

    def _render_full_transcript(self):
        if not self.transcript:
            return "(empty)"
        out = []
        for entry in self.transcript:
            out.append(f"=== Turn {entry['turn']+1} : {entry['type']} ===")
            out.append(f"Query: {entry['query']}")
            if entry["type"] == "patient_query":
                sql = entry["sql_agent"]
                if isinstance(sql, dict) and "error" not in sql:
                    out.append("--- SQL agent ---")
                    out.append(f"SQL: {sql['sql']}")
                    out.append(f"Rows ({sql['n_rows']}, preview):")
                    for r in sql["rows_preview"][:5]:
                        out.append(f"  {r}")
                else:
                    out.append(f"--- SQL agent: {sql} ---")
                out.append("--- Vector DB ---")
                vec = entry["vector_db"]
                if isinstance(vec, list):
                    for h in vec[:5]:
                        out.append(
                            f"  [{h.get('source_table')}|score={h.get('score',0):.3f}|ts={h.get('timestamp','')}]"
                            f" {h.get('text','')[:FULL_VEC_CHARS]}"
                        )
                else:
                    out.append(f"  {vec}")
                # --- Discharge notes ---
                notes = entry.get("notes")
                out.append("--- Discharge notes ---")
                if notes is None:
                    out.append("  (not retrieved)")
                elif isinstance(notes, dict) and "error" in notes:
                    out.append(f"  ERROR: {notes['error']}")
                elif isinstance(notes, list):
                    if not notes:
                        out.append("  (no hits for this patient)")
                    else:
                        for h in notes[:5]:
                            sec = h.get("section_name") or "?"
                            out.append(
                                f"  [{sec}|hadm={h.get('hadm_id','?')}|d={h.get('distance',0):.3f}|ct={h.get('charttime','')}]"
                                f" {(h.get('text') or '')[:FULL_NOTES_CHARS]}"
                            )
            elif entry["type"] == "literature_query":
                hits = entry["literature"]
                if isinstance(hits, list):
                    for h in hits:
                        if "error" in h:
                            out.append(f"  ERROR: {h['error']}")
                        else:
                            title = h.get("title") or "?"
                            out.append(
                                f"  [{h['parent_block_id']}|{title[:60]}|doc={h['doc_id']}|score={h['score']:.3f}]"
                            )
                            out.append(f"  {h['text'][:FULL_LIT_CHARS]}")
            out.append("")
        return "\n".join(out)

    # ------------------------------------------------------------------
    def _load_vector_store(self, patient_db_root):
        from retrieve_ehr import load_store
        path = Path(patient_db_root) / f"subject_{self.subject_id}"
        if not path.exists():
            raise FileNotFoundError(f"No patient vector store at {path}")
        return load_store(path)

    def _vector_search(self, query, k):
        """run_query handles encoding the string query into a vector internally."""
        from retrieve_ehr import run_query
        return run_query(self.vector_store, query, k=k, verbose=False)

    def _save(self, result):
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        path = RUNS_DIR / f"{ts}_subject_{self.subject_id}.json"
        with open(path, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nSaved transcript to {path}")
        return path


def _extract_json(text):
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        return json.loads(m.group(1))
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    raise ValueError(f"No JSON in LLM output: {text[:200]}")