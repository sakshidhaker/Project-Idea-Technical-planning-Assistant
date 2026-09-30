# Fresh RAG request fix

Replace these two files in the project:

```text
backend/rag.py
backend/api/document_api.py
```

## What changed?

Every Chat/Creator request searches the current knowledge base again by creating a
new embedding for the current user request and ranking the knowledge chunks again.

The application keeps only the expensive document-embedding index in memory.
It does not keep the previous request's retrieved context as memory.

When Creator validation fails, the retry also performs a new RAG search instead of
reusing the first attempt's context.

## What did NOT change?

- No new database tables.
- No new model/router framework.
- No conversation-history database.
- No new frontend system.
- No re-embedding of every document for every question unless a knowledge file
  was added/changed.

## Replacement rule

These are full-file replacements. Do not paste individual functions into the
old versions because the teaching comments and function connections are meant to
stay together.
