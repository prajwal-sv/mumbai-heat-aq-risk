"""Settings and folder paths. One place, so the other files stay short."""
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
RAW_OPENAQ = ROOT / "data" / "raw" / "openaq"
RAW_NASA = ROOT / "data" / "raw" / "nasa_power"
CLEAN = ROOT / "data" / "clean"

load_dotenv(ROOT / ".env")


def load_config():
    """Read config.yaml into a dictionary."""
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_openaq_key():
    """Read the OpenAQ key from .env. Stops with a clear message if missing."""
    key = os.getenv("OPENAQ_API_KEY", "").strip()
    if not key or key == "paste_your_key_here":
        raise SystemExit("OpenAQ key not found. Put it in the .env file (see .env.example).")
    return key