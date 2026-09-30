# 09 — Testing and Debugging

## Automated tests

Run:

```bash
pytest -q
```

The tests exercise real SQLite CRUD, knowledge loading, semantic-search ranking with a deterministic test encoder, validator behavior, model-download control flow, and real PDF/DOCX file contents.

## Manual application test

1. Start with `python run.py`.
2. Open the browser.
3. Confirm the model download check appears in the terminal when the model is missing.
4. Create a normal account.
5. Log out and log in again.
6. Ask several questions about different knowledge topics.
7. Rephrase the same question and check that RAG still runs.
8. Create a PDF about a knowledge topic.
9. Create a DOCX about a different topic.
10. Log in as `admin@local.test` / `admin`.
11. Search users.
12. Delete a normal user.
13. Confirm the admin cannot delete itself.

## Debugging order

```text
Browser message
   ↓
Flask terminal
   ↓
API route
   ↓
RAG/model stage
   ↓
artifact renderer
```

The teaching edition intentionally uses short stage/message/suggestion responses instead of a large exception framework.
