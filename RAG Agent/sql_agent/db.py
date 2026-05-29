"""PostgreSQL connection with statement_timeout enforced."""
import psycopg2
from . import config


def get_connection():
    conn = psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        dbname=config.DB_NAME,
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"SET statement_timeout = {config.STATEMENT_TIMEOUT_MS}")
    conn.autocommit = False
    return conn
