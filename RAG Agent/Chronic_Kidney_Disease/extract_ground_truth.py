"""
Extract t1 ground truth for each subject in cohort_nodes.csv.
t1 = treatments/procedures during the node admission.
Output: ground_truth/subject_<sid>/{table_name}.csv
"""
from pathlib import Path
import pandas as pd

ROOT       = Path('/gpfs/data/razavianlab/capstone/2025_agentic/Chronic_Kidney_Disease')
COHORT_CSV = ROOT / 'cohort_nodes.csv'
SAMPLES    = ROOT / 'ckd_samples'
LOOKUP_DIR = ROOT / 'lookup_tables'
GT_OUT     = ROOT / 'ground_truth'
GT_OUT.mkdir(exist_ok=True)

# table_name -> (time_col, link)  link = 'hadm_id' or via parent join key
GT_TABLES = {
    'hosp.prescriptions':   ('starttime',  'hadm_id'),
    'hosp.pharmacy':        ('starttime',  'hadm_id'),
    'hosp.emar':            ('charttime',  'hadm_id'),
    'hosp.emar_detail':     (None,         'via_emar'),
    'hosp.procedures_icd':  ('chartdate',  'hadm_id'),
    'icu.procedureevents':  ('starttime',  'hadm_id'),
    'icu.inputevents':      ('starttime',  'hadm_id'),
}


def load_table(subject_dir, name):
    """Load CSV for a given table, returning empty df if absent."""
    csv = subject_dir / f'mimiciv_{name}.csv'
    if not csv.exists():
        return pd.DataFrame()
    return pd.read_csv(csv, dtype=str, low_memory=False)


def extract_for_subject(stage, sid, hadm_id, admit, disch, lookups):
    src = SAMPLES / stage / f'subject_{sid}'
    out = GT_OUT / f'subject_{sid}'
    out.mkdir(exist_ok=True)

    print(f"\n=== {stage}/subject_{sid} (hadm={hadm_id}, {admit}—{disch}) ===")

    # First pass: get emar_ids belonging to node admission (for emar_detail filter)
    emar = load_table(src, 'hosp.emar')
    if len(emar):
        emar = emar[emar['hadm_id'].astype(str) == str(hadm_id)]
        if 'charttime' in emar.columns:
            emar['charttime'] = pd.to_datetime(emar['charttime'], errors='coerce')
            emar = emar[(emar['charttime'] >= admit) & (emar['charttime'] <= disch)]
    emar_ids = set(emar['emar_id'].astype(str)) if 'emar_id' in emar.columns else set()

    summary = {}
    for name, (tcol, link) in GT_TABLES.items():
        df = load_table(src, name)
        if len(df) == 0:
            summary[name] = 0
            continue

        if link == 'hadm_id':
            df = df[df['hadm_id'].astype(str) == str(hadm_id)]
            if tcol and tcol in df.columns:
                df[tcol] = pd.to_datetime(df[tcol], errors='coerce')
                df = df[(df[tcol] >= admit) & (df[tcol] <= disch)]
        elif link == 'via_emar':
            if 'emar_id' in df.columns:
                df = df[df['emar_id'].astype(str).isin(emar_ids)]
            else:
                df = df.iloc[:0]

        # apply lookup joins for readability
        if name == 'hosp.procedures_icd' and len(df):
            df = df.merge(
                lookups['d_icd_procedures'][['icd_code','icd_version','long_title']],
                on=['icd_code','icd_version'], how='left'
            )
        if name in ('icu.procedureevents','icu.inputevents') and len(df):
            df = df.merge(
                lookups['d_items'][['itemid','label']], on='itemid', how='left'
            )

        summary[name] = len(df)
        if len(df):
            df.to_csv(out / f'{name}.csv', index=False)

    total = sum(summary.values())
    print(f"  total t1 rows: {total}")
    for name, n in summary.items():
        print(f"    {name}: {n}")
    return total


def load_lookups():
    out = {}
    for name in ('d_icd_procedures', 'd_items'):
        df = pd.read_parquet(LOOKUP_DIR / f'{name}.parquet')
        for col in ('itemid','icd_code','icd_version'):
            if col in df.columns:
                df[col] = df[col].astype(str)
        out[name] = df
    return out


def main():
    cohort = pd.read_csv(COHORT_CSV)
    cohort['node_admittime'] = pd.to_datetime(cohort['node_admittime'])
    cohort['node_dischtime'] = pd.to_datetime(cohort['node_dischtime'])

    lookups = load_lookups()
    print("Lookups loaded.")

    for _, row in cohort.iterrows():
        extract_for_subject(
            stage=row['stage'],
            sid=str(row['subject_id']),
            hadm_id=row['node_hadm_id'],
            admit=row['node_admittime'],
            disch=row['node_dischtime'],
            lookups=lookups,
        )


if __name__ == '__main__':
    main()