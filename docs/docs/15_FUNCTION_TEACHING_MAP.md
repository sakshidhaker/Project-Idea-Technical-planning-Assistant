# 15 — Function Teaching Map

This project is designed so a student can answer five questions while reading a function:

1. **What does it do?**
2. **Why does it exist?**
3. **Who calls it?**
4. **What does it call?**
5. **Where do I edit it?**

## Frontend JavaScript

`setupPage()`

- Purpose: connect browser forms/buttons.
- Called by: the browser when `DOMContentLoaded` fires.
- Calls: `sendChat()`, `createArtifact()`, `showMode()`, `newChat()`.
- Edit: `frontend/app.js` when adding browser-only interactions.

`postForm()`

- Purpose: send browser form data to Flask.
- Called by: `sendChat()` and `createArtifact()`.
- Calls: browser `fetch()`.
- Edit: change request transport/error display only.

`sendChat()`

- Purpose: send a chat message to Python and display its answer.
- Connection: `app.html -> app.js -> /api/chat -> chat_api.py`.
- Important: it does not run RAG or Qwen itself.

`createArtifact()`

- Purpose: send a document request and file type to Python.
- Connection: `app.html -> app.js -> /api/generate -> document_api.py`.
- Important: Python performs generation, validation, and file creation.

## Authentication

`signup()` in `backend/api/auth_api.py`

- Purpose: accept signup form data.
- Calls: `auth.py` validation and hashing, then `database.py` INSERT.
- Connection: `signup.html -> POST /api/auth/signup`.

`login()` in `backend/api/auth_api.py`

- Purpose: verify credentials and create a session.
- Calls: `database.get_user()` and `auth.check_password()`.
- Connection: `login.html -> POST /api/auth/login`.

## GenAI

`search_knowledge()` in `backend/rag.py`

- Purpose: semantic retrieval from `knowledge/*.txt`.
- Called by: Chat and Creator API routes.
- Calls: Sentence Transformers encoder and NumPy similarity.

`build_chat_prompt()` in `backend/ai.py`

- Purpose: join the question and retrieved context into instructions for Qwen.
- Called by: `generate_chat_response()`.

`build_document_prompt()` in `backend/ai.py`

- Purpose: create Creator instructions, including the small Python-generation rule.
- Called by: `document_api.py`.

`generate_text()` in `backend/ai.py`

- Purpose: run the local Qwen model.
- Calls: `load_model()` -> `llama_cpp.Llama`.

## Validation

`validate_generated_text()` in `backend/validator.py`

- Purpose: reject clearly bad output before file creation.
- Checks: length, structure, topic, and Python syntax for explicit Python-programming requests.
- Connection: `document_api.py -> validator -> one retry`.
