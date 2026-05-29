# """
# Chunk discharge notes for the CKD 8-case cohort with t_cutoff filtering.

# For each subject in cohort_nodes.csv, keep ONLY notes from admissions whose
# admittime < t_cutoff AND dischtime < t_cutoff -- i.e. admissions that had
# already completed (and therefore produced a discharge note) at the simulated
# decision point.

# Chunking logic (process_and_chunk + split_text_with_overlap + raw_top_30)
# is preserved 1:1 from the AKI version. Only cohort filtering + IO is changed.

# Outputs: ckd_8_chunks.jsonl
# """
# import re
# from pathlib import Path

# import pandas as pd
# from tqdm.auto import tqdm
# from transformers import AutoTokenizer

# # === Config ===
# DISCHARGE_CSV = "/gpfs/data/razavianlab/capstone/2025_agentic/mimic/Notes/physionet.org/files/mimic-iv-note/2.2/note/discharge.csv.gz"
# COHORT_CSV    = "/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/cohort_nodes.csv"
# SAMPLES_ROOT  = Path("/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/ckd_samples")
# OUTPUT_JSONL  = "/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/ckd_8_chunks.jsonl"


# # === 1. Tokenizer (global) ===
# print("Loading bge-m3 tokenizer...")
# bge_tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3")
# print("Tokenizer loaded successfully.")


# # === 2. Token/splitting helpers (1:1 from AKI version) ===
# def count_tokens_bge(text, tokenizer):
#     """
#     使用 bge-m3 的真实 tokenizer 计算 token 数量。
#     add_special_tokens=False 是因为我们只计算文本本身的 token 长度，
#     模型实际推理时会自动在头尾加上 [CLS] 和 [SEP]。
#     """
#     if not text.strip():
#         return 0
#     return len(tokenizer.encode(text, add_special_tokens=False))


# def split_text_with_overlap(text, tokenizer, max_tokens=1024, depth=0):
#     """
#     递归式句子切分，带防死循环极致保护。
#     """
#     if depth > 50:
#         return [text]

#     if count_tokens_bge(text, tokenizer) <= max_tokens:
#         return [text]

#     sentences = re.split(r'(?<=[.!?])\s+', text)

#     if len(sentences) <= 3:
#         words = text.split()
#         if len(words) <= 2:
#             return [text]

#         mid_w = len(words) // 2
#         overlap = min(10, max(1, mid_w // 2))

#         part1_text = " ".join(words[:mid_w + overlap])
#         part2_text = " ".join(words[mid_w - overlap:])

#         if len(part1_text) >= len(text) or len(part2_text) >= len(text):
#             part1_text = " ".join(words[:mid_w])
#             part2_text = " ".join(words[mid_w:])

#         return (split_text_with_overlap(part1_text, tokenizer, max_tokens, depth + 1) +
#                 split_text_with_overlap(part2_text, tokenizer, max_tokens, depth + 1))

#     mid_idx = len(sentences) // 2
#     part1_text = " ".join(sentences[:mid_idx + 1]).strip()
#     part2_text = " ".join(sentences[mid_idx - 1:]).strip()

#     if len(part1_text) >= len(text) or len(part2_text) >= len(text):
#         part1_text = " ".join(sentences[:mid_idx]).strip()
#         part2_text = " ".join(sentences[mid_idx:]).strip()

#     result = []
#     result.extend(split_text_with_overlap(part1_text, tokenizer, max_tokens, depth + 1))
#     result.extend(split_text_with_overlap(part2_text, tokenizer, max_tokens, depth + 1))
#     return result


# # === 3. Main chunking function (1:1 from AKI version) ===
# def process_and_chunk(df, text_col, raw_top_30, tokenizer=bge_tokenizer):
#     """
#     语义切分病历，完整保留所有元数据。
#     新增逻辑：对超过 1024 token 的 chunk 进行二次递归句段切分，并标注 part_N。
#     """
#     meta_cols = ['note_id', 'subject_id', 'hadm_id', 'note_type', 'note_seq', 'charttime', 'storetime']
#     available_meta = [c for c in meta_cols if c in df.columns]

#     clean_keywords = set()
#     for kw in raw_top_30:
#         k = " ".join(kw.replace('\n', ' ').split()).lower()
#         if k:
#             clean_keywords.add(k)

#     sorted_keywords = sorted(list(clean_keywords), key=len, reverse=True)

#     pattern_parts = [
#         '^' + re.escape(kw).replace(r'\ ', r'[\s\n]+') + r'[ \t]*:'
#         for kw in sorted_keywords
#     ]
#     master_regex = re.compile('|'.join(pattern_parts), re.MULTILINE | re.IGNORECASE)

#     all_chunks = []

#     def append_chunk_data(base_c_id, base_s_name, text_content):
#         sub_texts = split_text_with_overlap(text_content, tokenizer, max_tokens=1024)

#         if len(sub_texts) == 1:
#             chunk_data = {
#                 'chunk_id': base_c_id,
#                 'section_name': base_s_name,
#                 'chunk_text': sub_texts[0]
#             }
#             chunk_data.update({col: row[col] for col in available_meta})
#             all_chunks.append(chunk_data)
#         else:
#             for idx, sub_t in enumerate(sub_texts, 1):
#                 chunk_data = {
#                     'chunk_id': f"{base_c_id}_part_{idx}",
#                     'section_name': f"{base_s_name}_part_{idx}",
#                     'chunk_text': sub_t
#                 }
#                 chunk_data.update({col: row[col] for col in available_meta})
#                 all_chunks.append(chunk_data)

#     for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing Chunks"):
#         text = str(row[text_col])

#         sid = str(row.get('subject_id', 'unk')).lower()
#         nid = str(row.get('note_id', 'unk')).lower()
#         hid = str(row.get('hadm_id', 'unk')).lower()

#         matches = list(master_regex.finditer(text))

#         valid_matches = []
#         seen_sections = set()
#         for m in matches:
#             header_content = " ".join(m.group(0).strip().rstrip(':').replace('\n', ' ').split()).lower()
#             if header_content not in seen_sections:
#                 valid_matches.append((m.start(), m.end(), header_content))
#                 seen_sections.add(header_content)

#         if not valid_matches:
#             clean_chunk_text = " ".join(text.split())
#             base_c_id = f"{sid}_{nid}_{hid}_uncategorized"
#             base_s_name = 'uncategorized'
#             append_chunk_data(base_c_id, base_s_name, clean_chunk_text)
#             continue

#         valid_matches.sort(key=lambda x: x[0])

#         for i in range(len(valid_matches)):
#             start_idx, content_start, s_name = valid_matches[i]
#             end_idx = valid_matches[i + 1][0] if i + 1 < len(valid_matches) else len(text)

#             raw_content = text[content_start:end_idx].strip()

#             if raw_content:
#                 clean_chunk_text = " ".join(raw_content.split())
#                 safe_s_name = s_name.replace(' ', '_').replace('/', '_')
#                 base_c_id = f"{sid}_{nid}_{hid}_{safe_s_name}"
#                 append_chunk_data(base_c_id, s_name, clean_chunk_text)

#     return pd.DataFrame(all_chunks)


# # === 4. Top-30 schema list (1:1 from AKI version) ===
# raw_top_30 = [
#     "PAST MEDICAL HISTORY", "ALLERGIES", "FAMILY HISTORY", "FOLLOWUP INSTRUCTIONS",
#     "CHIEF COMPLAINT", "DISCHARGE DISPOSITION", "DISCHARGE INSTRUCTIONS",
#     "PERTINENT RESULTS", "DISCHARGE MEDICATIONS", "MEDICATIONS ON ADMISSION",
#     "PHYSICAL EXAM", "BRIEF HOSPITAL COURSE", "MAJOR SURGICAL OR INVASIVE PROCEDURE",
#     "SOCIAL HISTORY", "HISTORY OF PRESENT ILLNESS", "IMPRESSION",
#     "DISCHARGE CONDITION", "DISCHARGE DIAGNOSIS", "HOME\n \nDISCHARGE DIAGNOSIS",
#     "TRANSITIONAL ISSUES", "HOME WITH SERVICE\n \nFACILITY", "ADMISSION LABS",
#     "DISCHARGE LABS", "NONE\n\n \nHISTORY OF PRESENT ILLNESS", "ADMISSION PHYSICAL EXAM",
#     "DISCHARGE PHYSICAL EXAM", "EXTENDED CARE\n \nFACILITY", "IMAGING",
#     "CHRONIC ISSUES", "FINDINGS"
# ]


# # === 5. Build (subject_id, hadm_id) t0 set from cohort + per-subject admissions CSVs ===
# def build_t0_pairs(cohort_df):
#     """
#     For each (subject_id, t_cutoff) in cohort_nodes.csv, load that subject's
#     pre-sampled admissions CSV and collect (subject_id, hadm_id) pairs whose
#     admittime < cutoff AND dischtime < cutoff. These are admissions that had
#     already completed by the simulated decision point and therefore have a
#     valid discharge note available as past information.
#     """
#     pairs = set()
#     for _, row in cohort_df.iterrows():
#         sid = str(row['subject_id'])
#         stage = row['stage']
#         cutoff = pd.to_datetime(row['node_admittime'])
#         adm_csv = SAMPLES_ROOT / stage / f'subject_{sid}' / 'mimiciv_hosp.admissions.csv'
#         if not adm_csv.exists():
#             print(f"  WARN: missing admissions CSV for subject {sid} at {adm_csv}")
#             continue
#         adm = pd.read_csv(adm_csv, dtype=str)
#         adm['admittime'] = pd.to_datetime(adm['admittime'], errors='coerce')
#         adm['dischtime'] = pd.to_datetime(adm['dischtime'], errors='coerce')
#         valid = adm[(adm['admittime'] < cutoff) & (adm['dischtime'] < cutoff)]
#         n_total = len(adm)
#         n_valid = len(valid)
#         print(f"  subject {sid} ({stage}, cutoff={cutoff}): "
#               f"{n_valid}/{n_total} admissions fall fully in t0")
#         for hid in valid['hadm_id']:
#             pairs.add((sid, str(hid)))
#     return pairs


# # === 6. Main IO ===
# def main():
#     print(f"\nLoading cohort: {COHORT_CSV}")
#     cohort = pd.read_csv(COHORT_CSV)
#     print(f"  {len(cohort)} subjects in cohort")

#     print(f"\nBuilding t0 (subject_id, hadm_id) pairs from admissions CSVs...")
#     t0_pairs = build_t0_pairs(cohort)
#     print(f"  Total t0 (subject, hadm) pairs: {len(t0_pairs)}")
#     if not t0_pairs:
#         print("ERROR: no t0 pairs found. Check cohort_nodes.csv and admissions CSVs.")
#         return

#     cohort_subjects = set(p[0] for p in t0_pairs)

#     print(f"\nLoading discharge notes: {DISCHARGE_CSV}")
#     discharge = pd.read_csv(DISCHARGE_CSV, dtype=str)
#     print(f"  {len(discharge):,} total notes")

#     # First narrow by subject (cheap), then by (subject_id, hadm_id) pair
#     subj_filtered = discharge[discharge["subject_id"].isin(cohort_subjects)].copy()
#     print(f"  {len(subj_filtered):,} notes for cohort subjects (all times)")

#     keys = list(zip(subj_filtered["subject_id"].astype(str),
#                     subj_filtered["hadm_id"].astype(str)))
#     in_t0 = [k in t0_pairs for k in keys]
#     filtered = subj_filtered[in_t0].copy()
#     print(f"  {len(filtered):,} notes pass t0 filter "
#           f"(admittime AND dischtime < t_cutoff)")

#     if len(filtered) == 0:
#         print("ERROR: no notes matched cohort t0 hadm_ids. Check data sources.")
#         return

#     print("\nNotes per subject (t0):")
#     for sid, n in filtered.groupby("subject_id").size().items():
#         print(f"  {sid}: {n} notes")

#     print("\nChunking...")
#     df_chunks = process_and_chunk(filtered, text_col="text", raw_top_30=raw_top_30)

#     print(f"\nTotal chunks: {len(df_chunks):,}")
#     print(f"Unique chunk_ids: {df_chunks['chunk_id'].nunique():,}")

#     if df_chunks["chunk_id"].duplicated().any():
#         dupes = df_chunks["chunk_id"].duplicated().sum()
#         print(f"WARNING: {dupes} duplicate chunk_ids, deduping...")
#         df_chunks = df_chunks.drop_duplicates("chunk_id").reset_index(drop=True)
#         print(f"After dedup: {len(df_chunks):,}")

#     Path(OUTPUT_JSONL).parent.mkdir(parents=True, exist_ok=True)
#     df_chunks.to_json(OUTPUT_JSONL, orient="records", lines=True, force_ascii=False)
#     print(f"\nSaved to {OUTPUT_JSONL}")


# if __name__ == "__main__":
#     main()
"""
Chunk discharge notes for the CKD 8-case cohort with t_cutoff filtering.

For each subject in cohort_nodes.csv, keep ONLY notes from admissions whose
admittime < t_cutoff AND dischtime < t_cutoff -- i.e. admissions that had
already completed (and therefore produced a discharge note) at the simulated
decision point.

Chunking logic (process_and_chunk + split_text_with_overlap + raw_top_30)
is preserved 1:1 from the AKI version. Only cohort filtering + IO is changed.

Outputs: ckd_8_chunks.jsonl
"""
import re
from pathlib import Path

import pandas as pd
from tqdm.auto import tqdm
from transformers import AutoTokenizer

# === Config ===
DISCHARGE_CSV = "/gpfs/data/razavianlab/capstone/2025_agentic/mimic/Notes/physionet.org/files/mimic-iv-note/2.2/note/discharge.csv.gz"
COHORT_CSV    = "/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/cohort_nodes.csv"
SAMPLES_ROOT  = Path("/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/ckd_samples")
OUTPUT_JSONL  = "/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease/ckd_8_chunks.jsonl"


# === 1. Tokenizer (global) ===
print("Loading bge-m3 tokenizer...")
bge_tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3")
print("Tokenizer loaded successfully.")


# === 2. Token/splitting helpers (1:1 from AKI version) ===
def count_tokens_bge(text, tokenizer):
    """
    使用 bge-m3 的真实 tokenizer 计算 token 数量。
    add_special_tokens=False 是因为我们只计算文本本身的 token 长度，
    模型实际推理时会自动在头尾加上 [CLS] 和 [SEP]。
    """
    if not text.strip():
        return 0
    return len(tokenizer.encode(text, add_special_tokens=False))


def split_text_with_overlap(text, tokenizer, max_tokens=1024, depth=0):
    """
    递归式句子切分，带防死循环极致保护。
    """
    if depth > 50:
        return [text]

    if count_tokens_bge(text, tokenizer) <= max_tokens:
        return [text]

    sentences = re.split(r'(?<=[.!?])\s+', text)

    if len(sentences) <= 3:
        words = text.split()
        if len(words) <= 2:
            return [text]

        mid_w = len(words) // 2
        overlap = min(10, max(1, mid_w // 2))

        part1_text = " ".join(words[:mid_w + overlap])
        part2_text = " ".join(words[mid_w - overlap:])

        if len(part1_text) >= len(text) or len(part2_text) >= len(text):
            part1_text = " ".join(words[:mid_w])
            part2_text = " ".join(words[mid_w:])

        return (split_text_with_overlap(part1_text, tokenizer, max_tokens, depth + 1) +
                split_text_with_overlap(part2_text, tokenizer, max_tokens, depth + 1))

    mid_idx = len(sentences) // 2
    part1_text = " ".join(sentences[:mid_idx + 1]).strip()
    part2_text = " ".join(sentences[mid_idx - 1:]).strip()

    if len(part1_text) >= len(text) or len(part2_text) >= len(text):
        part1_text = " ".join(sentences[:mid_idx]).strip()
        part2_text = " ".join(sentences[mid_idx:]).strip()

    result = []
    result.extend(split_text_with_overlap(part1_text, tokenizer, max_tokens, depth + 1))
    result.extend(split_text_with_overlap(part2_text, tokenizer, max_tokens, depth + 1))
    return result


# === 3. Main chunking function (1:1 from AKI version) ===
def process_and_chunk(df, text_col, raw_top_30, tokenizer=bge_tokenizer):
    """
    语义切分病历，完整保留所有元数据。
    新增逻辑：对超过 1024 token 的 chunk 进行二次递归句段切分，并标注 part_N。
    """
    meta_cols = ['note_id', 'subject_id', 'hadm_id', 'note_type', 'note_seq', 'charttime', 'storetime']
    available_meta = [c for c in meta_cols if c in df.columns]

    clean_keywords = set()
    for kw in raw_top_30:
        k = " ".join(kw.replace('\n', ' ').split()).lower()
        if k:
            clean_keywords.add(k)

    sorted_keywords = sorted(list(clean_keywords), key=len, reverse=True)

    pattern_parts = [
        '^' + re.escape(kw).replace(r'\ ', r'[\s\n]+') + r'[ \t]*:'
        for kw in sorted_keywords
    ]
    master_regex = re.compile('|'.join(pattern_parts), re.MULTILINE | re.IGNORECASE)

    all_chunks = []

    # Threshold: a chunk must have at least this many real (non-redacted)
    # characters after stripping MIMIC's de-id placeholders, or it is dropped.
    # MIMIC replaces PHI with sequences of underscores like ___ or _________.
    # All-redacted chunks (e.g. "Attending: ___", "Discharge instructions: ___")
    # pollute retrieval — agent gets a top-k hit with no usable signal.
    MIN_REAL_CHARS = 30

    def real_char_count(text):
        """Characters left after removing underscore runs and whitespace."""
        # collapse any run of underscores, then strip
        stripped = re.sub(r'_+', '', text).strip()
        # also drop standalone punctuation that has no semantic content
        stripped = re.sub(r'\s+', ' ', stripped)
        return len(stripped)

    def append_chunk_data(base_c_id, base_s_name, text_content):
        sub_texts = split_text_with_overlap(text_content, tokenizer, max_tokens=1024)

        if len(sub_texts) == 1:
            if real_char_count(sub_texts[0]) < MIN_REAL_CHARS:
                return  # drop mostly-redacted chunk
            chunk_data = {
                'chunk_id': base_c_id,
                'section_name': base_s_name,
                'chunk_text': sub_texts[0]
            }
            chunk_data.update({col: row[col] for col in available_meta})
            all_chunks.append(chunk_data)
        else:
            for idx, sub_t in enumerate(sub_texts, 1):
                if real_char_count(sub_t) < MIN_REAL_CHARS:
                    continue  # drop mostly-redacted sub-chunk
                chunk_data = {
                    'chunk_id': f"{base_c_id}_part_{idx}",
                    'section_name': f"{base_s_name}_part_{idx}",
                    'chunk_text': sub_t
                }
                chunk_data.update({col: row[col] for col in available_meta})
                all_chunks.append(chunk_data)

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing Chunks"):
        text = str(row[text_col])

        sid = str(row.get('subject_id', 'unk')).lower()
        nid = str(row.get('note_id', 'unk')).lower()
        hid = str(row.get('hadm_id', 'unk')).lower()

        matches = list(master_regex.finditer(text))

        valid_matches = []
        seen_sections = set()
        for m in matches:
            header_content = " ".join(m.group(0).strip().rstrip(':').replace('\n', ' ').split()).lower()
            if header_content not in seen_sections:
                valid_matches.append((m.start(), m.end(), header_content))
                seen_sections.add(header_content)

        if not valid_matches:
            clean_chunk_text = " ".join(text.split())
            base_c_id = f"{sid}_{nid}_{hid}_uncategorized"
            base_s_name = 'uncategorized'
            append_chunk_data(base_c_id, base_s_name, clean_chunk_text)
            continue

        valid_matches.sort(key=lambda x: x[0])

        for i in range(len(valid_matches)):
            start_idx, content_start, s_name = valid_matches[i]
            end_idx = valid_matches[i + 1][0] if i + 1 < len(valid_matches) else len(text)

            raw_content = text[content_start:end_idx].strip()

            if raw_content:
                clean_chunk_text = " ".join(raw_content.split())
                safe_s_name = s_name.replace(' ', '_').replace('/', '_')
                base_c_id = f"{sid}_{nid}_{hid}_{safe_s_name}"
                append_chunk_data(base_c_id, s_name, clean_chunk_text)

    return pd.DataFrame(all_chunks)


# === 4. Top-30 schema list (1:1 from AKI version) ===
raw_top_30 = [
    "PAST MEDICAL HISTORY", "ALLERGIES", "FAMILY HISTORY", "FOLLOWUP INSTRUCTIONS",
    "CHIEF COMPLAINT", "DISCHARGE DISPOSITION", "DISCHARGE INSTRUCTIONS",
    "PERTINENT RESULTS", "DISCHARGE MEDICATIONS", "MEDICATIONS ON ADMISSION",
    "PHYSICAL EXAM", "BRIEF HOSPITAL COURSE", "MAJOR SURGICAL OR INVASIVE PROCEDURE",
    "SOCIAL HISTORY", "HISTORY OF PRESENT ILLNESS", "IMPRESSION",
    "DISCHARGE CONDITION", "DISCHARGE DIAGNOSIS", "HOME\n \nDISCHARGE DIAGNOSIS",
    "TRANSITIONAL ISSUES", "HOME WITH SERVICE\n \nFACILITY", "ADMISSION LABS",
    "DISCHARGE LABS", "NONE\n\n \nHISTORY OF PRESENT ILLNESS", "ADMISSION PHYSICAL EXAM",
    "DISCHARGE PHYSICAL EXAM", "EXTENDED CARE\n \nFACILITY", "IMAGING",
    "CHRONIC ISSUES", "FINDINGS"
]


# === 5. Build (subject_id, hadm_id) t0 set from cohort + per-subject admissions CSVs ===
def build_t0_pairs(cohort_df):
    """
    For each (subject_id, t_cutoff) in cohort_nodes.csv, load that subject's
    pre-sampled admissions CSV and collect (subject_id, hadm_id) pairs whose
    admittime < cutoff AND dischtime < cutoff. These are admissions that had
    already completed by the simulated decision point and therefore have a
    valid discharge note available as past information.
    """
    pairs = set()
    for _, row in cohort_df.iterrows():
        sid = str(row['subject_id'])
        stage = row['stage']
        cutoff = pd.to_datetime(row['node_admittime'])
        adm_csv = SAMPLES_ROOT / stage / f'subject_{sid}' / 'mimiciv_hosp.admissions.csv'
        if not adm_csv.exists():
            print(f"  WARN: missing admissions CSV for subject {sid} at {adm_csv}")
            continue
        adm = pd.read_csv(adm_csv, dtype=str)
        adm['admittime'] = pd.to_datetime(adm['admittime'], errors='coerce')
        adm['dischtime'] = pd.to_datetime(adm['dischtime'], errors='coerce')
        valid = adm[(adm['admittime'] < cutoff) & (adm['dischtime'] < cutoff)]
        n_total = len(adm)
        n_valid = len(valid)
        print(f"  subject {sid} ({stage}, cutoff={cutoff}): "
              f"{n_valid}/{n_total} admissions fall fully in t0")
        for hid in valid['hadm_id']:
            pairs.add((sid, str(hid)))
    return pairs


# === 6. Main IO ===
def main():
    print(f"\nLoading cohort: {COHORT_CSV}")
    cohort = pd.read_csv(COHORT_CSV)
    print(f"  {len(cohort)} subjects in cohort")

    print(f"\nBuilding t0 (subject_id, hadm_id) pairs from admissions CSVs...")
    t0_pairs = build_t0_pairs(cohort)
    print(f"  Total t0 (subject, hadm) pairs: {len(t0_pairs)}")
    if not t0_pairs:
        print("ERROR: no t0 pairs found. Check cohort_nodes.csv and admissions CSVs.")
        return

    cohort_subjects = set(p[0] for p in t0_pairs)

    print(f"\nLoading discharge notes: {DISCHARGE_CSV}")
    discharge = pd.read_csv(DISCHARGE_CSV, dtype=str)
    print(f"  {len(discharge):,} total notes")

    # First narrow by subject (cheap), then by (subject_id, hadm_id) pair
    subj_filtered = discharge[discharge["subject_id"].isin(cohort_subjects)].copy()
    print(f"  {len(subj_filtered):,} notes for cohort subjects (all times)")

    keys = list(zip(subj_filtered["subject_id"].astype(str),
                    subj_filtered["hadm_id"].astype(str)))
    in_t0 = [k in t0_pairs for k in keys]
    filtered = subj_filtered[in_t0].copy()
    print(f"  {len(filtered):,} notes pass t0 filter "
          f"(admittime AND dischtime < t_cutoff)")

    if len(filtered) == 0:
        print("ERROR: no notes matched cohort t0 hadm_ids. Check data sources.")
        return

    print("\nNotes per subject (t0):")
    for sid, n in filtered.groupby("subject_id").size().items():
        print(f"  {sid}: {n} notes")

    print("\nChunking...")
    df_chunks = process_and_chunk(filtered, text_col="text", raw_top_30=raw_top_30)

    print(f"\nTotal chunks: {len(df_chunks):,}")
    print(f"Unique chunk_ids: {df_chunks['chunk_id'].nunique():,}")

    if df_chunks["chunk_id"].duplicated().any():
        dupes = df_chunks["chunk_id"].duplicated().sum()
        print(f"WARNING: {dupes} duplicate chunk_ids, deduping...")
        df_chunks = df_chunks.drop_duplicates("chunk_id").reset_index(drop=True)
        print(f"After dedup: {len(df_chunks):,}")

    Path(OUTPUT_JSONL).parent.mkdir(parents=True, exist_ok=True)
    df_chunks.to_json(OUTPUT_JSONL, orient="records", lines=True, force_ascii=False)
    print(f"\nSaved to {OUTPUT_JSONL}")


if __name__ == "__main__":
    main()