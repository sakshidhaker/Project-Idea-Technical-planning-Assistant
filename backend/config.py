"""Paths and small settings. Edit model / admin defaults here (or in .env)."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # python-dotenv is optional
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent.parent
if load_dotenv:
    load_dotenv(BASE_DIR / ".env")

DB_PATH = BASE_DIR / "data" / "app.db"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
MODELS_DIR = BASE_DIR / "models"
GENERATED_DIR = BASE_DIR / "generated"
for _d in (DB_PATH.parent, KNOWLEDGE_DIR, MODELS_DIR, GENERATED_DIR):
    _d.mkdir(parents=True, exist_ok=True)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@local.test").lower()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

# To use a bigger, smarter model just change these 3 lines in .env (see docs/UPGRADE_MODEL.md)
MODEL_REPO = os.getenv("MODEL_REPO", "Qwen/Qwen2.5-0.5B-Instruct-GGUF")
MODEL_FILE = os.getenv("MODEL_FILE", "qwen2.5-0.5b-instruct-q4_k_m.gguf")
MODEL_LABEL = os.getenv("MODEL_LABEL", "Qwen 2.5 Instruct 0.5B")
N_CTX = 4096
MAX_TOKENS = 700

# multilingual: understands Hindi + English (Hinglish works through query expansion in rag.py)
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
RAG_BACKEND = os.getenv("RAG_BACKEND", "auto").lower()


# --- deployment switches (Render / cloud) ---
# ENABLE_LLM=0 -> "lite mode": no local model, answers come from the knowledge base only
ENABLE_LLM = os.getenv("ENABLE_LLM", "1").strip().lower() not in ("0", "false", "no")
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0").strip() == "1"
