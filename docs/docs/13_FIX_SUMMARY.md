# 13 — Fix Summary

## Frontend

The browser layer remains intentionally small.

- `frontend/app.js` handles browser events, reads form values, sends requests, and displays Python results.
- It does not perform RAG, Qwen inference, validation, database work, or document generation.
- Admin search/delete remain normal Flask/Jinja forms.
- Function-level comments now explain purpose, caller, connection, and edit location.

## Imports and teaching comments

Important Python files now explain why each imported library/function is needed. The same files use function-level teaching notes so students can trace the flow from route -> helper -> result.

## Admin

The built-in account is:

```text
email:    admin@local.test
password: admin
```

`ensure_admin_account()` runs at application startup and ensures the known local demo login works with the current SQLite database.

## Automatic model download

Startup calls `ensure_model_downloaded()`. If the configured GGUF is missing, Hugging Face Hub downloads it automatically. If the network is unavailable, the UI/database can still start and the AI request reports the model-download problem clearly.

## Python generation

This version intentionally focuses reliable Creator programming generation on Python instead of introducing a multi-language generation framework.

Improvements:

- stronger Python code examples in `knowledge/`;
- common Python request patterns and game examples;
- clearer Python generation instructions in `backend/ai.py`;
- a small Python syntax/import validator in `backend/validator.py`;
- a tiny Python-specific semantic retrieval hint in `backend/rag.py`.

## Document creation

The pipeline remains:

```text
RAG -> Qwen -> validator -> one retry -> PDF/DOCX
```

The document renderers stay separate and simple.
