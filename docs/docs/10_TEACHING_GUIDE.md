# 10 — Teaching Guide

## Suggested teaching order

1. HTML structure
2. CSS layout
3. Jinja values
4. Flask routes
5. SQLite CRUD
6. Authentication + hashing
7. RAG basics
8. Embeddings and semantic retrieval
9. Local Qwen through llama.cpp
10. Validation and one retry
11. PDF/DOCX generation
12. End-to-end demo

## Reading one feature

Use Chat as the main example:

```text
app.html
 ↓
app.js
 ↓
chat_api.py
 ↓
rag.py
 ↓
ai.py
```

Students can understand the complete path without opening the whole project.

## Teaching principle

Avoid clever syntax when a basic loop, variable, or `if` statement is clearer. The goal is to understand the connection between modules before learning Python shortcuts.
