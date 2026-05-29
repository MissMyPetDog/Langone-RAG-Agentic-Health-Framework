"""Schema introspection (information_schema) + YAML metadata loader."""
import yaml
import pandas as pd


def introspect(conn, schemas):
    """Return DataFrame of all columns across given schemas."""
    placeholders = ",".join(f"'{s}'" for s in schemas)
    sql = f"""
        SELECT table_schema, table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema IN ({placeholders})
        ORDER BY table_schema, table_name, ordinal_position;
    """
    return pd.read_sql(sql, conn)


def load_metadata(path):
    with open(path) as f:
        return yaml.safe_load(f)


def render_schema_text(metadata, introspected_df):
    """Combine YAML metadata + auto-introspected columns into a single text block."""
    lines = ["# GLOBAL NOTES (NYU deployment quirks)"]
    for note in metadata.get("_global_notes", []):
        lines.append(f"- {note}")

    yaml_keys = {(t["schema"], t["table"]) for t in metadata.get("tables", [])}

    lines.append("\n# TABLES")
    for t in metadata.get("tables", []):
        lines.append(_format_table(t))

    intro_keys = set(zip(introspected_df.table_schema, introspected_df.table_name))
    missing = sorted(intro_keys - yaml_keys)
    if missing:
        lines.append("\n# TABLES WITHOUT METADATA (use cautiously, columns auto-detected)")
        for sch, tbl in missing:
            cols = introspected_df[
                (introspected_df.table_schema == sch)
                & (introspected_df.table_name == tbl)
            ]
            col_str = ", ".join(f"{r.column_name}({r.data_type})" for _, r in cols.iterrows())
            lines.append(f"- {sch}.{tbl}: {col_str}")
    return "\n".join(lines)


def _format_table(t):
    out = [f"\n## {t['schema']}.{t['table']}"]
    if t.get("description"):
        out.append(t["description"].strip())
    if t.get("primary_key"):
        out.append(f"PK: {', '.join(t['primary_key'])}")
    if t.get("patient_link"):
        out.append(f"Patient filter column: {t['patient_link']}")
    if t.get("joins"):
        for j in t["joins"]:
            on = ", ".join(j.get("on", []))
            purpose = f" -- {j['purpose']}" if j.get("purpose") else ""
            out.append(f"JOIN {j['to']} ON ({on}){purpose}")
    if t.get("columns"):
        out.append("Columns:")
        for c in t["columns"]:
            desc = c.get("desc", "")
            sep = ": " if desc else ""
            out.append(f"  - {c['name']} ({c['type']}){sep}{desc}")
    if t.get("notes"):
        out.append("Notes:")
        for n in t["notes"]:
            out.append(f"  - {n}")
    return "\n".join(out)
