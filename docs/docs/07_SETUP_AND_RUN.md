# 07 — Setup and Run

## Standard setup

```bash
python -m venv .venv
```

Linux/macOS/WSL:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Start:

```bash
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

## Automatic model download

On startup, Python checks for the configured GGUF. If it is missing, `backend/ai.py` downloads it directly from the configured Hugging Face repository. No manual copy into `models/` is required.

If startup cannot reach Hugging Face, the app still starts so the login/database UI remains available. The next Chat/Create request retries the download.

The first RAG request also downloads the Sentence Transformers embedding model through its normal model-loading process.

## Admin demo

```text
Email: admin@local.test
Password: admin
```

The admin account is recreated/updated at startup from the local configuration so a stale teaching database does not leave the demo login broken.

## Existing old database

This teaching edition intentionally uses a different schema from the older production-style project. For a clean teaching run, use a fresh project `data/app.db`. Do not copy the old multi-table database into this edition.
