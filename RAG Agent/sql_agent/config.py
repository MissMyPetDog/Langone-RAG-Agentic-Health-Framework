"""Configuration. Edit KONG_API_KEY before first run."""
import os
from pathlib import Path

ROOT = Path(__file__).parent
METADATA_PATH = ROOT / "metadata.yaml"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# --- Database ---
DB_HOST = os.getenv("MIMIC_DB_HOST", "cl40s-8014")
DB_PORT = int(os.getenv("MIMIC_DB_PORT", "6543"))
DB_USER = os.getenv("PGUSER")  # falls back to libpq default (PGUSER / OS user) if unset
DB_NAME = os.getenv("MIMIC_DB_NAME", "postgres")
SCHEMAS = ["mimiciv_hosp", "mimiciv_icu", "mimiciv_ed"]
STATEMENT_TIMEOUT_MS = 60000

# --- LLM (NYU Kong GPT-4o) ---
KONG_API_KEY = "N/A"  # <<< fill in
BASE_URL = "https://kong-api.prod1.nyumc.org/gpt-4o/v1.3.0"
MODEL = "gpt-4o"

# --- Agent behavior ---
DEFAULT_LIMIT = 1000
MAX_RETRIES = 2
