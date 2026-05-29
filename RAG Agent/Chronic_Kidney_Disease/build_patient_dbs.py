"""
build_patient_dbs.py
For each subject in cohort_nodes.csv, build a vector store of all data
strictly before that subject's t_cutoff (node_admittime).
Output: patient_db/subject_<sid>/
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, "/gpfs/data/razavianlab/capstone/2025_agentic/agentic_workflow")
sys.path.insert(0, "/gpfs/data/razavianlab/capstone/2025_agentic")
from retrieve_ehr import SimpleStore, save_store, encode_texts
from sql_agent import db

ROOT       = Path('/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease')
COHORT_CSV = ROOT / 'cohort_nodes.csv'
SAMPLES    = ROOT / 'ckd_samples'
LOOKUP_DIR = ROOT / 'lookup_tables'
DB_OUT     = ROOT / 'patient_db'
DB_OUT.mkdir(exist_ok=True)
LOOKUP_DIR.mkdir(exist_ok=True)

MODEL_NAME = "BAAI/bge-m3"

# ---- time-cutoff dispatch ----
DIRECT_TIME = {
    'hosp.admissions': 'admittime',
    'hosp.transfers': 'intime',
    'hosp.services': 'transfertime',
    'hosp.labevents': 'charttime',
    'hosp.microbiologyevents': 'charttime',
    'hosp.prescriptions': 'starttime',
    'hosp.pharmacy': 'starttime',
    'hosp.emar': 'charttime',
    'hosp.poe': 'ordertime',
    'hosp.omr': 'chartdate',
    'hosp.procedures_icd': 'chartdate',
    'hosp.hcpcsevents': 'chartdate',
    'icu.icustays': 'intime',
    'icu.chartevents': 'charttime',
    'icu.inputevents': 'starttime',
    'icu.outputevents': 'charttime',
    'icu.procedureevents': 'starttime',
    'icu.datetimeevents': 'charttime',
    'icu.ingredientevents': 'starttime',
    'ed.edstays': 'intime',
    'ed.medrecon': 'charttime',
    'ed.pyxis': 'charttime',
    'ed.vitalsign': 'charttime',
}
HADM_LINKED = {'hosp.diagnoses_icd', 'hosp.drgcodes'}
EMAR_LINKED = {'hosp.emar_detail'}
POE_LINKED  = {'hosp.poe_detail'}
ED_LINKED   = {'ed.diagnosis', 'ed.triage'}
STATIC      = {'hosp.patients'}

# ---- serialization (reused from AKI baseline) ----
GLOBAL_SKIP_COLS = {"row_id"}
NULL_STRINGS = {"\\N", "\\\\N", "___", "", "nan", "None"}
TIME_COL_PATTERNS = ["time", "date", "intime", "outtime"]

def find_timestamp(row_dict):
    for col, val in row_dict.items():
        if pd.isna(val): continue
        if any(p in col.lower() for p in TIME_COL_PATTERNS):
            return str(val), col
    return None, None

def serialize_row(source_table, row_dict):
    parts = [f"[source: {source_table}]"]
    for col, val in row_dict.items():
        if col in GLOBAL_SKIP_COLS: continue
        if pd.isna(val): continue
        sval = str(val).strip()
        if sval in NULL_STRINGS: continue
        parts.append(f"{col}: {sval}")
    return " | ".join(parts)

# ---- lookup table caching ----
def load_lookups():
    spec = {
        'd_labitems':       ('mimiciv_hosp', 'd_labitems'),
        'd_icd_diagnoses':  ('mimiciv_hosp', 'd_icd_diagnoses'),
        'd_icd_procedures': ('mimiciv_hosp', 'd_icd_procedures'),
        'd_hcpcs':          ('mimiciv_hosp', 'd_hcpcs'),
        'd_items':          ('mimiciv_icu',  'd_items'),
    }
    out, conn = {}, None
    for name, (sch, tbl) in spec.items():
        path = LOOKUP_DIR / f'{name}.parquet'
        if not path.exists():
            if conn is None:
                conn = db.get_connection()
                conn.autocommit = True
            print(f"Dumping {sch}.{tbl} -> {path.name}")
            pd.read_sql(f"SELECT * FROM {sch}.{tbl}", conn).to_parquet(path, index=False)
        df = pd.read_parquet(path)
        # match CSV string types for merge keys
        for col in ('itemid','icd_code','icd_version','code','hcpcs_cd'):
            if col in df.columns:
                df[col] = df[col].astype(str)
        out[name] = df
    if conn: conn.close()
    return out

# ---- lookup joins (reused from AKI baseline) ----
def left_merge(main, lookup, on, lookup_cols):
    if main is None or len(main) == 0: return main
    cols = on if isinstance(on, list) else [on]
    return main.merge(lookup[cols + lookup_cols], on=on, how='left')

def apply_lookups(tables, lookups):
    if 'hosp.labevents' in tables:
        tables['hosp.labevents'] = left_merge(tables['hosp.labevents'],
            lookups['d_labitems'], on='itemid', lookup_cols=['label'])
    if 'hosp.diagnoses_icd' in tables:
        tables['hosp.diagnoses_icd'] = left_merge(tables['hosp.diagnoses_icd'],
            lookups['d_icd_diagnoses'], on=['icd_code','icd_version'], lookup_cols=['long_title'])
    if 'hosp.procedures_icd' in tables:
        tables['hosp.procedures_icd'] = left_merge(tables['hosp.procedures_icd'],
            lookups['d_icd_procedures'], on=['icd_code','icd_version'], lookup_cols=['long_title'])
    if 'hosp.hcpcsevents' in tables and len(tables['hosp.hcpcsevents']) > 0:
        sub = lookups['d_hcpcs'][['code','long_description']].rename(columns={'code':'hcpcs_cd'})
        tables['hosp.hcpcsevents'] = tables['hosp.hcpcsevents'].merge(sub, on='hcpcs_cd', how='left')
    for t in ('icu.chartevents','icu.inputevents','icu.outputevents',
              'icu.procedureevents','icu.datetimeevents','icu.ingredientevents'):
        if t in tables and len(tables[t]) > 0:
            tables[t] = left_merge(tables[t], lookups['d_items'], on='itemid', lookup_cols=['label'])

# ---- cutoff filter ----
def collect_ids(tables, cutoff):
    def ids_from(tname, time_col, id_col):
        if tname not in tables: return set()
        df = tables[tname].copy()
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
        return set(df[df[time_col] < cutoff][id_col].astype(str))
    return (
        ids_from('hosp.admissions', 'admittime', 'hadm_id'),
        ids_from('hosp.emar',       'charttime', 'emar_id'),
        ids_from('hosp.poe',        'ordertime', 'poe_id'),
        ids_from('ed.edstays',      'intime',    'stay_id'),
    )

def filter_table(name, df, cutoff, hadms, emars, poes, ed_stays):
    if df is None or len(df) == 0: return df
    if name in STATIC: return df
    if name in DIRECT_TIME:
        col = DIRECT_TIME[name]
        if col not in df.columns: return df.iloc[:0]
        df = df.copy()
        df[col] = pd.to_datetime(df[col], errors='coerce')
        return df[df[col] < cutoff]
    if name in HADM_LINKED:
        return df[df['hadm_id'].astype(str).isin(hadms)] if 'hadm_id' in df.columns else df.iloc[:0]
    if name in EMAR_LINKED:
        return df[df['emar_id'].astype(str).isin(emars)] if 'emar_id' in df.columns else df.iloc[:0]
    if name in POE_LINKED:
        return df[df['poe_id'].astype(str).isin(poes)] if 'poe_id' in df.columns else df.iloc[:0]
    if name in ED_LINKED:
        return df[df['stay_id'].astype(str).isin(ed_stays)] if 'stay_id' in df.columns else df.iloc[:0]
    return df

# ---- per-subject builder ----
def build_for_subject(stage, sid, cutoff_str, lookups):
    src = SAMPLES / stage / f'subject_{sid}'
    out = DB_OUT / f'subject_{sid}'
    if out.exists():
        print(f"SKIP {sid}: already built at {out}")
        return

    cutoff = pd.to_datetime(cutoff_str)
    print(f"\n=== {stage}/subject_{sid} (cutoff={cutoff}) ===")

    tables = {}
    for csv in sorted(src.glob('mimiciv_*.csv')):
        name = csv.stem.replace('mimiciv_', '', 1)   # 'mimiciv_hosp.labevents' -> 'hosp.labevents'
        tables[name] = pd.read_csv(csv, dtype=str, low_memory=False)
    print(f"  loaded {len(tables)} tables")

    apply_lookups(tables, lookups)

    hadms, emars, poes, ed_stays = collect_ids(tables, cutoff)
    print(f"  pre-cutoff IDs: {len(hadms)} hadm, {len(emars)} emar, {len(poes)} poe, {len(ed_stays)} edstay")

    filtered = {}
    for name, df in tables.items():
        f = filter_table(name, df, cutoff, hadms, emars, poes, ed_stays)
        if f is not None and len(f) > 0:
            filtered[name] = f

    records = []
    for source_table, df in filtered.items():
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            text = serialize_row(source_table, row_dict)
            ts, ts_col = find_timestamp(row_dict)
            records.append({'source_table': source_table, 'text': text,
                            'timestamp': ts, 'time_col': ts_col, 'row_dict': row_dict})

    print(f"  records to encode: {len(records)}")
    if not records:
        print("  (empty t0, skipping)")
        return

    print(f"  encoding with {MODEL_NAME}...")
    vectors = encode_texts([r['text'] for r in records], MODEL_NAME)
    store = SimpleStore(vectors, records, model_name=MODEL_NAME)
    save_store(store, out, MODEL_NAME)
    print(f"  saved -> {out}")


def main():
    cohort = pd.read_csv(COHORT_CSV)
    print(f"Loading lookup tables...")
    lookups = load_lookups()
    print(f"Lookups: " + ", ".join(f"{k}({len(v)})" for k, v in lookups.items()))

    for _, row in cohort.iterrows():
        build_for_subject(row['stage'], str(row['subject_id']), row['node_admittime'], lookups)


if __name__ == '__main__':
    main()