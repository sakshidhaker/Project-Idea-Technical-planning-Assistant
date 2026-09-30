"""Run before a demo:  python check_setup.py   -> shows what is ready and what is missing."""
import importlib
import sys

from backend.config import DB_PATH, KNOWLEDGE_DIR, MODEL_FILE, MODELS_DIR

ok = True
def line(good, text, fix=""):
    global ok
    ok = ok and good
    print(("[OK]   " if good else "[FAIL] ") + text + ("" if good else f"   -> {fix}"))

line(sys.version_info[:2] >= (3, 10), f"Python {sys.version.split()[0]}", "use Python 3.10+ (3.11 recommended)")
for mod, pip in [("flask", "Flask"), ("dotenv", "python-dotenv"), ("numpy", "numpy"), ("sklearn", "scikit-learn"),
                 ("sentence_transformers", "sentence-transformers"), ("llama_cpp", "llama-cpp-python"),
                 ("reportlab", "reportlab"), ("docx", "python-docx"), ("huggingface_hub", "huggingface-hub")]:
    try:
        importlib.import_module(mod); line(True, f"package {pip}")
    except Exception as exc:
        line(False, f"package {pip} ({exc.__class__.__name__})", f"pip install {pip}")

model = MODELS_DIR / MODEL_FILE
line(model.exists(), f"model file {MODEL_FILE}" + (f" ({model.stat().st_size // 1_000_000} MB)" if model.exists() else ""),
     "put the .gguf in models/ or start the app once with internet")
n = len(list(KNOWLEDGE_DIR.glob("*.txt")))
line(n >= 10, f"{n} knowledge files", "add .txt files to knowledge/")
line(DB_PATH.parent.exists(), f"database folder {DB_PATH.parent}", "create the data/ folder")

try:
    from backend import rag
    info = rag.index_info()
    line(info["chunks"] > 0, f"RAG index: {info['chunks']} chunks, engine = {info['engine']}",
         "check knowledge/ files")
    if info["engine"] == "tfidf":
        print("[INFO] Using TF-IDF search. Hindi/Hinglish search is better with the multilingual embedding model "
              "(needs internet once to download ~470 MB).")
except Exception as exc:
    line(False, f"RAG failed: {exc}", "read the error above")

print("\nAll good. Run: python run.py" if ok else "\nFix the [FAIL] lines above, then run again.")
