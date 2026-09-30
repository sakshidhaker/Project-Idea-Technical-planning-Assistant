# 01 — Project Overview

## Goal

AI Creator Engine is a teaching product rather than a fake chatbot demo. A student can see a natural-language request travel through Flask, RAG, a local LLM, validation, and finally a downloadable artifact.

## Core capabilities

### Chat

The user sends a question. Python searches the prepared knowledge files semantically, builds a context section, sends the request plus context to Qwen, and returns the answer.

### Creator

The user describes a document, chooses PDF or DOCX, and Python runs the same RAG + Qwen path before validating and rendering the final file.

### Authentication

Signup uses name/email/password. Passwords are hashed before SQLite storage. Login creates a Flask session containing only the user ID.

### Admin

The single configured admin can search and delete users. The Admin page is server-rendered with Jinja, so JavaScript is not needed for database work.

## Mental model

```text
User
 ↓
HTML/Jinja
 ↓
Flask route
 ↓
Python validation
 ↓
RAG retrieval
 ↓
Qwen
 ↓
Validator
 ↓
PDF/DOCX
 ↓
Browser download
```

## Official references

- Python: https://docs.python.org/3/
- Flask: https://flask.palletsprojects.com/
- Jinja: https://jinja.palletsprojects.com/
- SQLite: https://www.sqlite.org/docs.html
- MDN Web Docs: https://developer.mozilla.org/en-US/docs/Web
