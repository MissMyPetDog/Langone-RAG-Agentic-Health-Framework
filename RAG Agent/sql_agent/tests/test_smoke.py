"""Smoke tests. Run from parent dir of sql_agent/:
   python -m sql_agent.tests.test_smoke
"""
from ..agent import SQLAgent

CASES = [
    ("How many alive patients have any CKD diagnosis?", None),
    ("How many CKD patients per stage?", None),
    ("Average age of alive female patients", None),
    ("List all diagnoses for this patient with their long titles", 11814360),
    ("How many ICU stays does this patient have?", 11814360),
    ("Show creatinine values for this patient ordered by time", 11814360),
    ("Top 10 most common ICD-10 diagnoses overall", None),
    ("Count of patients who died in hospital", None),
]


def main():
    agent = SQLAgent()
    for q, sid in CASES:
        try:
            r = agent.ask(q, sid)
            print(f"OK  | {q[:55]:55s} | {r['n_rows']:5d} rows | "
                  f"{r['attempts']} attempt(s) | {r['duration_ms']:5d} ms")
        except Exception as e:
            print(f"ERR | {q[:55]:55s} | {str(e)[:80]}")


if __name__ == "__main__":
    main()
