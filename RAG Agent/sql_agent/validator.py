"""SQL safety: only SELECT/WITH, no DDL/DML, enforce LIMIT."""
import re

FORBIDDEN = {"INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER",
             "CREATE", "GRANT", "REVOKE", "VACUUM", "COPY"}


def validate(sql):
    """Return cleaned SQL or raise ValueError."""
    s = sql.strip().rstrip(";")
    if ";" in s:
        raise ValueError("Multiple statements not allowed")
    upper = s.upper()
    first = re.match(r"\s*(\w+)", upper).group(1)
    if first not in {"SELECT", "WITH"}:
        raise ValueError(f"Only SELECT/WITH allowed, got: {first}")
    for kw in FORBIDDEN:
        if re.search(rf"\b{kw}\b", upper):
            raise ValueError(f"Forbidden keyword: {kw}")
    return s


def enforce_limit(sql, max_rows):
    if re.search(r"\blimit\s+\d+\b", sql, re.IGNORECASE):
        return sql
    return f"{sql}\nLIMIT {max_rows}"
