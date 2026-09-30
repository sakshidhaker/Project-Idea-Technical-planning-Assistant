# 03 — Code Edit Map

Use this table when you want to change one part without searching the whole project.

| I want to change... | Edit this |
| --- | --- |
| login fields/text | `frontend/login.html` |
| signup fields/text | `frontend/signup.html` |
| Chat/Create layout | `frontend/app.html` |
| Admin layout/table | `frontend/admin.html` |
| browser interactions | `frontend/app.js` |
| colors/layout/spacing | `frontend/style.css` |
| password rules | `backend/auth.py` |
| admin email/password defaults | `backend/config.py` |
| users table/SQL | `backend/database.py` |
| admin search/delete rules | `backend/admin.py` |
| model repository/file | `backend/config.py` |
| automatic model download | `backend/ai.py` |
| Chat prompt | `backend/ai.py` |
| Creator prompt / Python-generation rule | `backend/ai.py` |
| RAG loading/chunking/search | `backend/rag.py` |
| RAG source material | `knowledge/*.txt` |
| Python code validation | `backend/validator.py` |
| PDF appearance | `backend/pdf_generator.py` |
| DOCX appearance | `backend/docx_generator.py` |
| Chat HTTP route | `backend/api/chat_api.py` |
| Creator HTTP route | `backend/api/document_api.py` |
| login/signup HTTP routes | `backend/api/auth_api.py` |
| file download route | `backend/api/downloads_api.py` |
| page routing/startup | `backend/main.py` |
| startup command | `run.py` |

## Chat connection

```text
frontend/app.html
    ↓
frontend/app.js: sendChat()
    ↓ POST /api/chat
backend/api/chat_api.py: chat()
    ↓
backend/rag.py: search_knowledge() + get_context()
    ↓
backend/ai.py: build_chat_prompt() + generate_text()
    ↓
Qwen
    ↓
JSON
    ↓
frontend/app.js: addMessage()
```

## Creator connection

```text
frontend/app.html
    ↓
frontend/app.js: createArtifact()
    ↓ POST /api/generate
backend/api/document_api.py: generate()
    ↓
rag.py
    ↓
ai.py: build_document_prompt() + generate_text()
    ↓
validator.py
    ↓ one retry when needed
pdf_generator.py OR docx_generator.py
    ↓
generated/
    ↓
frontend/app.js: showResult()
```

## Authentication connection

```text
login.html / signup.html
    ↓ normal HTML form
api/auth_api.py
    ↓
auth.py
    ↓
database.py
    ↓
SQLite users
```
