# 02 — Architecture

## Main rule

One file has one understandable responsibility.

```text
frontend/app.html
    ↓
frontend/app.js
    ↓
backend/api/chat_api.py
    ↓
backend/rag.py
    ↓
backend/ai.py
    ↓
Qwen
```

Creator uses the same path and then calls `validator.py` followed by one of the artifact generators.

## Backend map

| File | Responsibility |
| --- | --- |
| `backend/main.py` | Flask app, Jinja pages, startup wiring |
| `backend/config.py` | paths and small settings |
| `backend/auth.py` | password rules, session, admin identity |
| `backend/database.py` | all SQLite SQL |
| `backend/admin.py` | admin behavior |
| `backend/rag.py` | load/chunk/embed/search knowledge |
| `backend/ai.py` | download/load/run Qwen and build prompts |
| `backend/validator.py` | general generation checks |
| `backend/pdf_generator.py` | PDF output |
| `backend/docx_generator.py` | DOCX output |
| `backend/api/auth_api.py` | login/signup/logout forms |
| `backend/api/chat_api.py` | Chat endpoint |
| `backend/api/document_api.py` | Creator endpoint |
| `backend/api/downloads_api.py` | file download endpoint |

## Frontend map

- `login.html` — email/password form
- `signup.html` — name/email/password form
- `app.html` — Chat + Create UI
- `admin.html` — server-rendered user table
- `app.js` — only browser interaction and transport
- `style.css` — shared visual styling

## Why JavaScript stays small

The browser should not know how to run RAG, choose models, validate content, calculate embeddings, or create PDFs. JavaScript only reads user input, sends it to Python, and displays Python's response.

Jinja renders stable server values such as the logged-in user and model status before the page reaches the browser.
