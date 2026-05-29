"""CLI: python -m sql_agent.cli ask 'question' [--subject-id N] [--time-cutoff TS] [--dry-run] [--json]"""
import argparse
import json
import sys

import pandas as pd

from .agent import SQLAgent


def main():
    p = argparse.ArgumentParser(prog="sql_agent")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("ask", help="Run one natural-language query")
    a.add_argument("question")
    a.add_argument("--subject-id", default=None)
    a.add_argument("--time-cutoff", default=None,
                   help="Restrict to data strictly before this timestamp (e.g. '2180-07-12 18:26:00')")
    a.add_argument("--dry-run", action="store_true")
    a.add_argument("--json", action="store_true")

    args = p.parse_args()

    if args.cmd == "ask":
        agent = SQLAgent()
        if args.dry_run:
            try:
                sql = agent.generate_sql_only(args.question, args.subject_id, args.time_cutoff)
            except Exception as e:
                print(f"ERROR: {e}", file=sys.stderr)
                sys.exit(1)
            print(sql)
            return

        try:
            result = agent.ask(args.question, args.subject_id, args.time_cutoff)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

        if args.json:
            print(json.dumps(result, default=str, indent=2))
        else:
            print(f"--- SQL ---\n{result['sql']}\n")
            print(f"--- Result ({result['n_rows']} rows | {result['duration_ms']} ms | "
                  f"{result['attempts']} attempt(s)) ---")
            if result["rows"]:
                print(pd.DataFrame(result["rows"]).to_string(index=False))


if __name__ == "__main__":
    main()