"""
Streamlit viewer for CKD orchestrator transcripts.

Usage on NYU Langone:
    # 1. On a compute node (or login node):
    cd /gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease
    /gpfs/scratch/zh1461/conda_envs/hf_env/bin/streamlit run viewer.py \
        --server.address 0.0.0.0 --server.port 8501

    # 2. On your laptop, open an SSH tunnel:
    ssh -L 8501:<compute-node-name>:8501 zh1461@<jump-host>

    # 3. Open http://localhost:8501 in your browser.

Override runs dir via env var if needed:
    CKD_RUNS_DIR=/some/other/path streamlit run viewer.py
"""
import json
import os
from pathlib import Path

import streamlit as st


# =====================================================================
# Config
# =====================================================================
DEFAULT_RUNS_DIR = (
    "/gpfs/data/razavianlab/capstone/2025_agentic/"
    "Chronic_Kidney_Disease/orchestrator/runs"
)
RUNS_DIR = Path(os.environ.get("CKD_RUNS_DIR", DEFAULT_RUNS_DIR))

st.set_page_config(page_title="CKD Agentic RAG", layout="wide")


# =====================================================================
# Render helpers for each retrieval source
# =====================================================================
def render_sql(sa):
    if isinstance(sa, dict) and "error" in sa:
        st.error(f"SQL error: {sa['error'][:500]}")
        return
    if not isinstance(sa, dict):
        st.caption("_no data_")
        return
    n_rows = sa.get("n_rows", 0)
    duration = sa.get("duration_ms", 0)
    st.caption(f"**{n_rows}** rows · {duration} ms · {sa.get('attempts', 1)} attempts")
    sql = sa.get("sql", "")
    if sql:
        st.code(sql, language="sql")
    rows = sa.get("rows_preview", [])
    if rows:
        st.dataframe(rows[:20], use_container_width=True)
        if len(rows) > 20:
            st.caption(f"_showing first 20 of {len(rows)} rows_")
    else:
        st.caption("_no rows returned_")


def render_vector(vec):
    if isinstance(vec, dict) and "error" in vec:
        st.error(f"Vector error: {vec['error'][:500]}")
        return
    if not isinstance(vec, list) or not vec:
        st.caption("_no hits_")
        return
    for i, h in enumerate(vec[:5], 1):
        st.markdown(
            f"**#{i}** `{h.get('source_table','?')}` · "
            f"cos={h.get('score',0):.3f} · ts={h.get('timestamp','?')}"
        )
        st.text(h.get("text", ""))


def render_notes(notes):
    if isinstance(notes, dict) and "error" in notes:
        st.error(f"Notes error: {notes['error'][:500]}")
        return
    if not isinstance(notes, list):
        st.caption("_not retrieved_")
        return
    if not notes:
        st.caption("_no hits — patient may have no completed prior admissions in t0_")
        return
    for i, h in enumerate(notes[:5], 1):
        st.markdown(
            f"**#{i}** `{h.get('section_name','?')}` · "
            f"hadm={h.get('hadm_id','?')} · dist={h.get('distance',0):.3f}"
        )
        st.text(h.get("text", "")[:1500])


def render_literature(hits):
    if not isinstance(hits, list) or not hits:
        st.caption("_no hits_")
        return
    for i, h in enumerate(hits[:5], 1):
        if isinstance(h, dict) and "error" in h:
            st.error(f"Lit error: {h['error'][:500]}")
            continue
        title = h.get("title", "?")
        block_id = h.get("parent_block_id", "?")
        score = h.get("score", 0)
        st.markdown(f"**#{i}** {title} · `{block_id}` · cos={score:.3f}")
        st.text(h.get("text", "")[:1500])


# =====================================================================
# Sidebar: select run
# =====================================================================
st.sidebar.title("CKD Agentic RAG")
st.sidebar.caption("Transcript viewer")

if not RUNS_DIR.exists():
    st.error(f"Runs directory not found:\n`{RUNS_DIR}`")
    st.info("Set the `CKD_RUNS_DIR` env var, or edit `DEFAULT_RUNS_DIR` in this file.")
    st.stop()

files = sorted(RUNS_DIR.glob("*.json"), reverse=True)
if not files:
    st.error(f"No JSON files in `{RUNS_DIR}`")
    st.stop()


@st.cache_data
def load_label(filepath_str):
    """Read just enough to build a sidebar label without loading full JSON each time."""
    try:
        d = json.loads(Path(filepath_str).read_text())
        sid = d.get("subject_id", "?")
        stage = d.get("stage", "?")
        ts = Path(filepath_str).stem.split("_subject_")[0]
        return f"{sid}  |  {stage}  |  {ts}"
    except Exception:
        return Path(filepath_str).name


labels = [load_label(str(f)) for f in files]
chosen_idx = st.sidebar.selectbox(
    "Select case",
    range(len(files)),
    format_func=lambda i: labels[i],
)
chosen_file = files[chosen_idx]
d = json.loads(chosen_file.read_text())

st.sidebar.markdown("---")
st.sidebar.caption(f"{len(files)} total runs")
st.sidebar.caption(f"file: `{chosen_file.name}`")


# =====================================================================
# Main: header
# =====================================================================
st.title(f"Subject {d['subject_id']}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("CKD stage", d.get("stage", "?"))
c2.metric("Turns used", d.get("n_turns_used", 0))
c3.metric("Duration (s)", f"{d.get('duration_sec', 0):.1f}")
c4.metric("t_cutoff", str(d.get("t_cutoff", "?"))[:10])


# =====================================================================
# Tabs: reasoning trace · patient summary · recommendation
# =====================================================================
tab_trans, tab_summary, tab_recommend = st.tabs(
    ["🔄 Agent reasoning trace", "📋 Patient summary", "💊 Recommendation"]
)


# ---- Reasoning trace ----
with tab_trans:
    transcript = d.get("transcript", [])
    if not transcript:
        st.info("Empty transcript.")

    # Quick action summary at top
    actions = [e.get("type", "?") for e in transcript]
    n_patient = actions.count("patient_query")
    n_literature = actions.count("literature_query")
    st.caption(
        f"**{len(transcript)} turns** · "
        f"🔍 {n_patient} patient queries · "
        f"📚 {n_literature} literature queries"
    )
    st.markdown("---")

    for entry in transcript:
        turn_n = entry["turn"] + 1
        etype = entry["type"]
        query = entry.get("query", "")

        if etype == "patient_query":
            icon = "🔍"
            type_label = "query_patient"
        elif etype == "literature_query":
            icon = "📚"
            type_label = "query_literature"
        else:
            icon = "❓"
            type_label = etype

        label = f"**T{turn_n}** · {icon} `{type_label}` · {query[:90]}"

        with st.expander(label, expanded=False):
            thought = entry.get("thought", "")
            if thought:
                st.info(f"💭 **Thought:** {thought}")
            if etype == "patient_query":
                st.markdown("##### 🗄️ SQL agent")
                render_sql(entry.get("sql_agent", {}))
                st.markdown("---")
                st.markdown("##### 🧠 Patient vector DB")
                render_vector(entry.get("vector_db", []))
                st.markdown("---")
                st.markdown("##### 📄 Discharge notes")
                render_notes(entry.get("notes", []))
            elif etype == "literature_query":
                render_literature(entry.get("literature", []))

    # Final thought (why the agent decided to stop / finalize)
    final_thought = d.get("final_thought", "")
    if final_thought:
        st.markdown("---")
        st.markdown("##### 🏁 Final thought (why finalize)")
        st.success(final_thought)


# ---- Patient summary ----
with tab_summary:
    st.markdown(d.get("patient_summary", "_not generated_"))


# ---- Recommendation ----
with tab_recommend:
    st.markdown(d.get("recommendation", "_not generated_"))