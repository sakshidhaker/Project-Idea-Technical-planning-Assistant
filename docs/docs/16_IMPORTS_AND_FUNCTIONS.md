# 16 — Imports and Function Teaching Map

Every important Python file has comments immediately around its imports. The goal is that a beginner can answer: **“Why is this here?”** before reading the function body.

## Example import map

`backend/ai.py`

```text
threading.Lock
    → prevents two model loads/generations from happening at the same time.

backend.config
    → supplies the model filename, repository, model folder, and generation limits.

backend.exceptions.ModelError
    → gives the UI a readable model/download/generation failure.
```

`backend/rag.py`

```text
numpy
    → stores embeddings and performs vector similarity.

backend.config
    → supplies chunk size, embedding model, top-k, and context limits.

RAGError
    → explains a retrieval failure to the API layer.
```

`backend/auth.py`

```text
flask.session
    → remembers which user is logged in.

werkzeug.security
    → hashes and checks passwords securely.

backend.database
    → reads/writes the one users table.
```

`backend/document_api.py`

```text
secrets
    → creates a random output filename.

Path
    → checks that the generated file is really inside generated/.

Flask request/jsonify
    → receives browser form data and returns JSON.

ai.py
    → generates the document text.

rag.py
    → supplies knowledge context.

validator.py
    → decides whether the generated content should become a file.

pdf_generator.py/docx_generator.py
    → create the requested artifact format.
```

## Function questions

For every important function, read the nearby teaching comments and ask:

```text
WHAT does it do?
WHY does it exist?
WHO calls it?
WHAT does it call?
WHAT does it return?
WHERE should I edit it?
```

This is why `frontend/app.js` comments sit directly above functions such as `sendChat()` and `createArtifact()`, while Python comments sit beside both imports and functions.
