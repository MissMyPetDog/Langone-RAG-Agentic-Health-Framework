"""
retrieve_ehr.py
================
Reusable retrieval module for persisted EHR vector stores.

Two modes:
  1. As a library (import in notebook):
       from retrieve_ehr import load_store, run_query, run_all_queries
       store = load_store("./stores/sapbert_stay33665686")
       run_all_queries(store, k=15, lambda_param=0.5)

  2. As a CLI script:
       python retrieve_ehr.py ./stores/bgem3_stay33665686 --k 20 --lambda 0.5
       python retrieve_ehr.py ./stores/bgem3_stay33665686 --store
       python retrieve_ehr.py ./stores/bgem3_stay33665686 --store --output-dir ./results

Score format:
    Each result is a (metadata, scores_dict) tuple where scores_dict has:
        - cosine: similarity to query
        - redundancy: max similarity to already-selected results
        - mmr: final MMR score that determined ranking
"""

import argparse
import csv
import json
import pickle
import re
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel


# ============================================================
# Default queries
# ============================================================

DEFAULT_QUERIES = [
    "how many times have this patient been admitted for acute kidney injuiry?",
    "what are the treatments during the patient's acute kidney injury?",
    "what are the lab results showing the patiant's kidney function?",
    "what medications were given to this patient during acute kidney injuiry",
    "what are the procedures given during the ICU stay",
    "Acute Kidney Injuiry (AKI)"
]


# ============================================================
# Vector store
# ============================================================

def _filter_indices_by_table(metadata, exclude_tables=None, include_tables=None):
    if not exclude_tables and not include_tables:
        return None

    exclude_set = set(exclude_tables) if exclude_tables else set()
    include_set = set(include_tables) if include_tables else None

    eligible = []
    for i, meta in enumerate(metadata):
        t = meta["source_table"]
        if include_set is not None and t not in include_set:
            continue
        if t in exclude_set:
            continue
        eligible.append(i)
    return np.array(eligible, dtype=np.int64)


class SimpleStore:
    """In-memory vector store with cosine similarity search."""

    def __init__(self, vectors, metadata, model_name=None):
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        self.vectors = vectors / np.clip(norms, 1e-12, None)
        self.metadata = metadata
        self.model_name = model_name

    def search(self, query_vec, k=20, exclude_tables=None, include_tables=None):
        q = query_vec / np.clip(np.linalg.norm(query_vec), 1e-12, None)
        sims = self.vectors @ q

        eligible_idx = _filter_indices_by_table(
            self.metadata, exclude_tables, include_tables
        )
        if eligible_idx is None:
            top_idx = np.argsort(-sims)[:k]
        else:
            eligible_sims = sims[eligible_idx]
            order = np.argsort(-eligible_sims)[:k]
            top_idx = eligible_idx[order]

        results = []
        for i in top_idx:
            cosine = float(sims[i])
            results.append((
                self.metadata[i],
                {"cosine": cosine, "redundancy": 0.0, "mmr": cosine},
            ))
        return results


def save_store(store, save_dir, model_name):
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    np.save(save_dir / "vectors.npy", store.vectors)
    with open(save_dir / "metadata.pkl", "wb") as f:
        pickle.dump(store.metadata, f)
    with open(save_dir / "model_name.txt", "w") as f:
        f.write(model_name)
    print(f"Saved {len(store.metadata)} rows to {save_dir}")


def load_store(save_dir):
    save_dir = Path(save_dir)
    vectors = np.load(save_dir / "vectors.npy")
    with open(save_dir / "metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    with open(save_dir / "model_name.txt") as f:
        model_name = f.read().strip()

    store = SimpleStore(vectors, metadata, model_name=model_name)
    print(
        f"Loaded {len(metadata)} rows from {save_dir} "
        f"(dim={vectors.shape[1]}, model={model_name})"
    )
    return store


# ============================================================
# Encoder management with caching
# ============================================================

_ENCODER_CACHE = {}


def get_encoder(model_name):
    if model_name in _ENCODER_CACHE:
        return _ENCODER_CACHE[model_name]

    print(f"Loading encoder: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device).eval()
    print(f"  device: {device}")

    _ENCODER_CACHE[model_name] = (tokenizer, model, device)
    return tokenizer, model, device


def encode_texts(texts, model_name, batch_size=64, max_length=512, show_progress=True):
    tokenizer, model, device = get_encoder(model_name)

    iterator = range(0, len(texts), batch_size)
    if show_progress and len(texts) > batch_size:
        try:
            from tqdm.auto import tqdm
            iterator = tqdm(iterator, desc=f"Encoding ({model_name.split('/')[-1]})")
        except ImportError:
            pass

    all_vectors = []
    for i in iterator:
        batch = texts[i:i + batch_size]
        inputs = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        ).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        vectors = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        all_vectors.append(vectors)
    return np.vstack(all_vectors)


# ============================================================
# Retrieval (cosine + MMR)
# ============================================================

def mmr_search(store, query_vec, k=15, lambda_param=0.5, fetch_k=None,
               exclude_tables=None, include_tables=None):
    q_norm = query_vec / np.clip(np.linalg.norm(query_vec), 1e-12, None)
    sims_to_query = store.vectors @ q_norm

    eligible_idx = _filter_indices_by_table(
        store.metadata, exclude_tables, include_tables
    )

    if eligible_idx is None:
        if fetch_k is None:
            fetch_k = min(k * 10, len(store.metadata))
        candidate_idx = np.argsort(-sims_to_query)[:fetch_k].tolist()
    else:
        if fetch_k is None:
            fetch_k = min(k * 10, len(eligible_idx))
        eligible_sims = sims_to_query[eligible_idx]
        order = np.argsort(-eligible_sims)[:fetch_k]
        candidate_idx = eligible_idx[order].tolist()

    selected_idx = []
    selected_results = []
    while len(selected_results) < k and candidate_idx:
        if not selected_idx:
            best_pos = 0
            chosen_idx = candidate_idx[best_pos]
            cosine = float(sims_to_query[chosen_idx])
            redundancy = 0.0
            mmr_score = lambda_param * cosine
        else:
            cand_vectors = store.vectors[candidate_idx]
            sel_vectors = store.vectors[selected_idx]
            sims_to_selected = cand_vectors @ sel_vectors.T
            max_sim_to_selected = sims_to_selected.max(axis=1)
            cand_relevance = sims_to_query[candidate_idx]
            mmr_scores = (
                lambda_param * cand_relevance
                - (1 - lambda_param) * max_sim_to_selected
            )
            best_pos = int(np.argmax(mmr_scores))
            chosen_idx = candidate_idx[best_pos]
            cosine = float(cand_relevance[best_pos])
            redundancy = float(max_sim_to_selected[best_pos])
            mmr_score = float(mmr_scores[best_pos])

        candidate_idx.pop(best_pos)
        selected_idx.append(chosen_idx)
        selected_results.append((
            store.metadata[chosen_idx],
            {"cosine": cosine, "redundancy": redundancy, "mmr": mmr_score},
        ))
    return selected_results


# ============================================================
# Query interface
# ============================================================

def run_query(store, query, k=15, lambda_param=1.0, verbose=True,
              exclude_tables=None, include_tables=None):
    if store.model_name is None:
        raise ValueError(
            "Store has no model_name attached. "
            "Make sure you loaded it via load_store()."
        )

    q_vec = encode_texts([query], store.model_name)[0]

    if lambda_param < 1.0:
        results = mmr_search(
            store, q_vec, k=k, lambda_param=lambda_param,
            exclude_tables=exclude_tables, include_tables=include_tables,
        )
        mode = f"MMR(lambda={lambda_param})"
    else:
        results = store.search(
            q_vec, k=k,
            exclude_tables=exclude_tables, include_tables=include_tables,
        )
        mode = "Cosine"

    if exclude_tables:
        mode += f" | excluded={exclude_tables}"
    if include_tables:
        mode += f" | included_only={include_tables}"

    if verbose:
        _print_results(query, results, mode, k)

    return results


def run_all_queries(store, queries=None, k=15, lambda_param=1.0,
                    exclude_tables=None, include_tables=None):
    if queries is None:
        queries = DEFAULT_QUERIES
    all_results = {}
    for q in queries:
        all_results[q] = run_query(
            store, q, k=k, lambda_param=lambda_param,
            exclude_tables=exclude_tables, include_tables=include_tables,
        )
    return all_results


def _print_results(query, results, mode, k):
    table_counts = {}
    for meta, _scores in results:
        t = meta["source_table"]
        table_counts[t] = table_counts.get(t, 0) + 1

    print(f"\n{'=' * 80}")
    print(f"Query: {query}  |  {mode}")
    print("=" * 80)
    print(f"\nTop-{k} table distribution:")
    for t, c in sorted(table_counts.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")

    print(f"\nTop-{k} results:")
    for rank, (meta, scores) in enumerate(results, 1):
        text_preview = meta["text"].replace("\n", " ")
        ts = meta.get("timestamp") or "no-ts"
        print(
            f"\n  [{rank}] cos={scores['cosine']:.3f} | "
            f"redund={scores['redundancy']:.3f} | "
            f"mmr={scores['mmr']:.3f} | "
            f"{meta['source_table']} | t={ts}"
        )
        print(f"      {text_preview}")


# ============================================================
# CSV / JSON export
# ============================================================

def _extract_subject_id(store):
    """Get subject_id from the first row's row_dict."""
    if not store.metadata:
        return None
    first = store.metadata[0]
    rd = first.get("row_dict", {})
    sid = rd.get("subject_id")
    if sid is not None:
        return str(sid)
    return None


def _extract_stay_id_from_path(store_dir):
    """Parse stay_id from store dir name like 'bgem3_v2_lookup_clean_stay33665686'."""
    name = Path(store_dir).name
    m = re.search(r"stay(\d+)", name)
    if m:
        return m.group(1)
    return None


def _safe_filename(name):
    """Convert 'hosp.labevents' -> 'hosp.labevents' (keep dots; just strip slashes)."""
    return name.replace("/", "_").replace("\\", "_")


def save_results(all_results, output_root, subject_id, stay_id, queries,
                 run_config=None):
    """
    Save retrieval results as:
        CASE{subject_id}_stay_id_{stay_id}_retrieved_results/
          ├─ queries.txt          # human-readable query list + config
          ├─ results.json         # complete raw output (all scores, configs, row_dict)
          ├─ query_1/
          │    ├─ ranking.csv               # rank, scores, source_table, table_row_idx, timestamp
          │    ├─ all_rows.csv              # full overview: all retrieved rows + scores + row_dict (JSON)
          │    ├─ hosp.diagnoses_icd.csv    # one CSV per source_table (row_dict columns)
          │    ├─ icu.procedureevents.csv
          │    └─ ...
          ├─ query_2/
          └─ ...

    Per-table CSV columns = union of row_dict keys across rows from that table
    (in this query). Rows align with table_row_idx in ranking.csv.
    all_rows.csv has row_dict serialized as JSON in one column (since columns
    differ across tables).
    """
    folder_name = f"CASE{subject_id}_stay_id_{stay_id}_retrieved_results"
    out_dir = Path(output_root) / folder_name
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- 1) queries.txt ----
    with open(out_dir / "queries.txt", "w") as f:
        if run_config:
            f.write("# Run config\n")
            for k, v in run_config.items():
                f.write(f"# {k}: {v}\n")
            f.write("\n")
        f.write("# Queries\n")
        for i, q in enumerate(queries, 1):
            f.write(f"query_{i}: {q}\n")

    # ---- 2) results.json (complete raw) ----
    json_payload = {
        "config": dict(run_config) if run_config else {},
        "queries": [],
    }
    for query_idx, (query_text, results) in enumerate(all_results.items(), 1):
        query_block = {
            "query_idx": query_idx,
            "query_text": query_text,
            "results": [],
        }
        for rank, (meta, scores) in enumerate(results, 1):
            query_block["results"].append({
                "rank": rank,
                "scores": scores,
                "source_table": meta["source_table"],
                "timestamp": meta.get("timestamp"),
                "time_col": meta.get("time_col"),
                "text": meta["text"],
                "row_dict": meta.get("row_dict", {}),
            })
        json_payload["queries"].append(query_block)

    with open(out_dir / "results.json", "w") as f:
        json.dump(json_payload, f, indent=2, default=str)

    # ---- 3) per-query subfolders with ranking.csv + per-table CSVs ----
    for query_idx, (query_text, results) in enumerate(all_results.items(), 1):
        q_dir = out_dir / f"query_{query_idx}"
        q_dir.mkdir(parents=True, exist_ok=True)

        # Group rows by source_table, remembering original rank for ranking.csv
        # Each entry in by_table: list of (rank, scores, meta)
        by_table = {}
        for rank, (meta, scores) in enumerate(results, 1):
            t = meta["source_table"]
            by_table.setdefault(t, []).append((rank, scores, meta))

        # Write per-table CSVs and build ranking entries
        # ranking_entries: list of (rank, cosine, redundancy, mmr, source_table,
        #                          table_row_idx, timestamp, time_col)
        ranking_entries = []
        # Map (table, rank_in_query) -> table_row_idx
        for table, rows in by_table.items():
            # union of row_dict keys (preserve first-seen order)
            seen_keys = []
            seen_set = set()
            for _r, _s, m in rows:
                for k_ in m.get("row_dict", {}).keys():
                    if k_ not in seen_set:
                        seen_set.add(k_)
                        seen_keys.append(k_)

            csv_path = q_dir / f"{_safe_filename(table)}.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(seen_keys)
                for table_row_idx, (rank, scores, meta) in enumerate(rows):
                    rd = meta.get("row_dict", {})
                    writer.writerow([rd.get(k_, "") for k_ in seen_keys])
                    ranking_entries.append({
                        "rank": rank,
                        "cosine": scores["cosine"],
                        "redundancy": scores["redundancy"],
                        "mmr": scores["mmr"],
                        "source_table": table,
                        "table_row_idx": table_row_idx,
                        "timestamp": meta.get("timestamp") or "",
                        "time_col": meta.get("time_col") or "",
                    })

        # Sort ranking_entries back by original rank, then write ranking.csv
        ranking_entries.sort(key=lambda r: r["rank"])
        with open(q_dir / "ranking.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "rank", "cosine", "redundancy", "mmr",
                "source_table", "table_row_idx", "timestamp", "time_col",
            ])
            for r in ranking_entries:
                writer.writerow([
                    r["rank"],
                    f"{r['cosine']:.6f}",
                    f"{r['redundancy']:.6f}",
                    f"{r['mmr']:.6f}",
                    r["source_table"],
                    r["table_row_idx"],
                    r["timestamp"],
                    r["time_col"],
                ])

        # Write all_rows.csv: full overview, one row per retrieved row,
        # with row_dict serialized as JSON since columns differ across tables.
        with open(q_dir / "all_rows.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "rank", "cosine", "redundancy", "mmr",
                "source_table", "timestamp", "time_col",
                "text", "row_dict_json",
            ])
            for rank, (meta, scores) in enumerate(results, 1):
                writer.writerow([
                    rank,
                    f"{scores['cosine']:.6f}",
                    f"{scores['redundancy']:.6f}",
                    f"{scores['mmr']:.6f}",
                    meta["source_table"],
                    meta.get("timestamp") or "",
                    meta.get("time_col") or "",
                    meta["text"],
                    json.dumps(meta.get("row_dict", {}), default=str),
                ])

    print(f"\nSaved {len(all_results)} query results to {out_dir}")
    return out_dir


# ============================================================
# CLI
# ============================================================

def _parse_args():
    parser = argparse.ArgumentParser(
        description="Retrieve from a persisted EHR vector store.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python retrieve_ehr.py ./stores/bgem3_stay33665686 --k 20 --lambda 0.5\n"
            "  python retrieve_ehr.py ./stores/bgem3_stay33665686 --store\n"
            "  python retrieve_ehr.py ./stores/bgem3_stay33665686 --store --output-dir ./results\n"
        ),
    )
    parser.add_argument("store_dir", help="Path to the saved vector store.")
    parser.add_argument("--k", type=int, default=15)
    parser.add_argument("--lambda", dest="lambda_param", type=float, default=1.0)
    parser.add_argument("--queries", nargs="+", default=None)
    parser.add_argument("--exclude-tables", nargs="+", default=None)
    parser.add_argument("--include-tables", nargs="+", default=None)
    parser.add_argument(
        "--store", action="store_true",
        help="Save retrieval results to CASE{subject_id}_stay_id_{stay_id}_retrieved_results/",
    )
    parser.add_argument(
        "--output-dir", default=".",
        help="Where to put the result folder (default: current dir).",
    )
    parser.add_argument(
        "--stay-id", default=None,
        help="Override stay_id (otherwise parsed from store dir name).",
    )
    return parser.parse_args()


def main():
    args = _parse_args()
    store = load_store(args.store_dir)
    queries = args.queries if args.queries else DEFAULT_QUERIES
    all_results = run_all_queries(
        store,
        queries=queries,
        k=args.k,
        lambda_param=args.lambda_param,
        exclude_tables=args.exclude_tables,
        include_tables=args.include_tables,
    )

    if args.store:
        subject_id = _extract_subject_id(store)
        stay_id = args.stay_id or _extract_stay_id_from_path(args.store_dir)

        if subject_id is None:
            print("WARNING: could not extract subject_id from store metadata. Skipping save.")
            return
        if stay_id is None:
            print("WARNING: could not extract stay_id from path. Use --stay-id to set it.")
            return

        run_config = {
            "store_dir": args.store_dir,
            "k": args.k,
            "lambda": args.lambda_param,
            "exclude_tables": args.exclude_tables,
            "include_tables": args.include_tables,
            "model_name": store.model_name,
            "subject_id": subject_id,
            "stay_id": stay_id,
        }
        save_results(
            all_results,
            output_root=args.output_dir,
            subject_id=subject_id,
            stay_id=stay_id,
            queries=queries,
            run_config=run_config,
        )


if __name__ == "__main__":
    main()