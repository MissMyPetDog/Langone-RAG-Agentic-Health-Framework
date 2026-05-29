"""SQLAgent: stateless natural-language to SQL agent for MIMIC-IV."""
import json
import re
import time
from datetime import datetime

import pandas as pd
import psycopg2

from . import config, db, llm, schema, validator


SYSTEM_TEMPLATE = """You are a PostgreSQL query writer for MIMIC-IV at NYU Langone.

Output exactly ONE SQL statement (SELECT or WITH...SELECT) wrapped in ```sql ... ``` fences.
No INSERT/UPDATE/DELETE/DDL. No commentary outside the fences.
Always schema-qualify tables (e.g., mimiciv_hosp.patients).

If the user provides a subject_id, restrict the query to that patient using the
patient_link column documented for the relevant table(s).

If the user provides a time_cutoff, you MUST filter every patient-event table so
that its primary time column is strictly less than time_cutoff. Use these columns:
  - labevents, microbiologyevents, chartevents, datetimeevents, outputevents, emar: charttime
  - prescriptions, pharmacy, inputevents, procedureevents, ingredientevents: starttime
  - admissions: admittime
  - transfers: intime
  - procedures_icd, hcpcsevents, omr: chartdate
  - diagnoses_icd: JOIN admissions and filter on admittime
  - emar_detail: JOIN emar and filter on emar.charttime
  - patients: NO time filter (static demographics)
For tables without an obvious time column, omit the filter on that table.

==== SCHEMA ====
{schema}
"""


class SQLAgent:
    def __init__(self):
        self.conn = db.get_connection()
        self.llm = llm.get_client()
        meta = schema.load_metadata(config.METADATA_PATH)
        intro = schema.introspect(self.conn, config.SCHEMAS)
        self.system_prompt = SYSTEM_TEMPLATE.format(
            schema=schema.render_schema_text(meta, intro)
        )

    def ask(self, question, subject_id=None, time_cutoff=None):
        """Run one query. Returns dict with sql, rows, columns, n_rows, duration_ms, attempts, error."""
        user_msg = self._format_user_message(question, subject_id, time_cutoff)
        start = time.time()
        last_sql = None
        last_err = None
        for attempt in range(config.MAX_RETRIES + 1):
            raw = llm.chat(self.llm, self.system_prompt, user_msg)
            try:
                sql = validator.validate(self._extract_sql(raw))
                sql = validator.enforce_limit(sql, config.DEFAULT_LIMIT)
                last_sql = sql
                df = pd.read_sql(sql, self.conn)
            except (ValueError, psycopg2.Error) as e:
                last_err = str(e).strip()
                self._safe_rollback()
                user_msg = (
                    "Previous SQL attempt failed.\n"
                    f"```sql\n{last_sql or '<extraction failed>'}\n```\n"
                    f"Error: {last_err}\n"
                    "Return a corrected SQL only."
                )
                continue
            result = {
                "sql": sql,
                "rows": df.to_dict(orient="records"),
                "columns": list(df.columns),
                "n_rows": len(df),
                "duration_ms": int((time.time() - start) * 1000),
                "attempts": attempt + 1,
                "error": None,
            }
            self._log(question, subject_id, time_cutoff, result)
            return result

        result = {
            "sql": last_sql, "rows": [], "columns": [],
            "n_rows": 0,
            "duration_ms": int((time.time() - start) * 1000),
            "attempts": config.MAX_RETRIES + 1,
            "error": last_err,
        }
        self._log(question, subject_id, time_cutoff, result)
        raise RuntimeError(f"Failed after {config.MAX_RETRIES + 1} attempts: {last_err}")

    def generate_sql_only(self, question, subject_id=None, time_cutoff=None):
        user_msg = self._format_user_message(question, subject_id, time_cutoff)
        raw = llm.chat(self.llm, self.system_prompt, user_msg)
        sql = validator.validate(self._extract_sql(raw))
        return validator.enforce_limit(sql, config.DEFAULT_LIMIT)

    @staticmethod
    def _format_user_message(question, subject_id, time_cutoff):
        parts = []
        if subject_id is not None:
            parts.append(f"subject_id = '{subject_id}'")
        if time_cutoff is not None:
            parts.append(f"time_cutoff = '{time_cutoff}'")
        parts.append(f"Question: {question}")
        return "\n".join(parts)

    @staticmethod
    def _extract_sql(text):
        m = re.search(r"```sql\s*(.+?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip()
        m = re.search(r"(?is)\b(WITH|SELECT)\b.+", text)
        if m:
            return m.group(0).strip()
        raise ValueError(f"No SQL found in LLM output: {text[:200]}")

    def _safe_rollback(self):
        try:
            self.conn.rollback()
        except Exception:
            pass

    def _log(self, question, subject_id, time_cutoff, result):
        entry = {
            "ts": datetime.utcnow().isoformat(),
            "question": question,
            "subject_id": subject_id,
            "time_cutoff": str(time_cutoff) if time_cutoff is not None else None,
            "sql": result.get("sql"),
            "n_rows": result.get("n_rows"),
            "duration_ms": result.get("duration_ms"),
            "attempts": result.get("attempts"),
            "error": result.get("error"),
        }
        log_file = config.LOG_DIR / f"{datetime.utcnow():%Y%m%d}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")