# 04 — Frontend Teaching Guide

## Design rule

The frontend is deliberately thin. Jinja/HTML handles page structure, and a small amount of JavaScript handles browser interactions that benefit from a live page.

## JavaScript responsibilities

`frontend/app.js`:

- reads form values;
- creates FormData;
- sends data to Flask using fetch();
- receives JSON;
- updates visible DOM text;
- switches the Chat/Create panels.

It does **not** perform:

- RAG calculations;
- embeddings;
- AI inference;
- validation;
- database queries;
- PDF/DOCX generation.

## Example connection

```text
Chat textarea
    ↓
sendChat()
    ↓
POST /api/chat
    ↓
backend/api/chat_api.py
    ↓
rag.py + ai.py
```

## Why forms are used for login/admin

Login, signup, logout, and Admin search/delete do not need JavaScript. Normal HTML forms send the data to Flask, and Jinja renders the next page.
