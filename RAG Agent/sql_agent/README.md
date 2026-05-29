# SQL Agent for MIMIC-IV @ NYU Langone

Stateless natural-language → PostgreSQL SQL agent. Each `ask()` call is independent;
orchestrators handle conversation state.

## Setup

1. Edit `config.py`: set `KONG_API_KEY` and (if needed) `DB_USER`.
2. Install deps: `pip install -r requirements.txt`.

## Usage

### CLI
```bash
# Cohort-level question
python -m sql_agent.cli ask "How many CKD patients per stage?"

# Patient-level question
python -m sql_agent.cli ask "creatinine trend" --subject-id 11814360

# Generate SQL only, do not execute
python -m sql_agent.cli ask "..." --dry-run

# JSON output (for orchestrator)
python -m sql_agent.cli ask "..." --json
```

Run from the parent directory of `sql_agent/`.

### Python API
```python
from sql_agent import SQLAgent

agent = SQLAgent()
result = agent.ask("How many CKD patients?")          # cohort
result = agent.ask("List diagnoses", subject_id=12345) # patient

# result = {
#   'sql': str,
#   'rows': list[dict],
#   'columns': list[str],
#   'n_rows': int,
#   'duration_ms': int,
#   'attempts': int,
#   'error': None | str,
# }
```

## Layout

```
sql_agent/
├── config.py           # API key, DB params, paths
├── db.py               # psycopg2 connection w/ statement_timeout
├── llm.py              # NYU Kong GPT-4o client
├── schema.py           # information_schema introspection + YAML loader
├── metadata.yaml       # MIMIC-IV table descriptions (manual, full coverage)
├── validator.py        # SQL safety (SELECT-only) + LIMIT enforcement
├── agent.py            # SQLAgent main class
├── cli.py              # terminal entry point
├── logs/               # JSONL per day: queries + outcomes
└── tests/test_smoke.py # 8 manual test cases
```

## Safety

- `SELECT` / `WITH` only; INSERT/UPDATE/DELETE/DDL all rejected.
- `statement_timeout = 30s` enforced server-side.
- `LIMIT 1000` auto-injected if not present.
- Self-correction up to 2 retries on errors (LLM sees the error and fixes).
- All calls logged to `logs/YYYYMMDD.jsonl`.

## Smoke test

```bash
python -m sql_agent.tests.test_smoke
```
