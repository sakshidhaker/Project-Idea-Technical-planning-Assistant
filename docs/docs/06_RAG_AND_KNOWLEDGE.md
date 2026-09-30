# 06 — RAG and Knowledge

## Real RAG path

```text
knowledge/*.txt
   ↓
load_knowledge()
   ↓
split_documents()
   ↓
Sentence Transformers embeddings
   ↓
vector similarity
   ↓
search_knowledge()
   ↓
get_context()
   ↓
ai.py prompt
   ↓
Qwen
```

The application does not keep a list of hardcoded questions. Natural-language queries are embedded and compared with knowledge chunks.

## Small Python retrieval trick

When a request clearly asks for a Python program/function, `search_knowledge()` adds a few Python-generation terms to the **semantic query**. The original request remains intact; the hint simply makes complete Python examples easier to retrieve.

This is intentionally small. It is not a replacement for embeddings or a new routing framework.

## Knowledge files

The project ships a broad set of prepared material plus focused Python generation files:

```text
41_python_code_generation_patterns.txt
42_python_games_and_small_programs.txt
43_python_generation_prompts.txt
44_python_debugging_and_code_quality.txt
```

These contain complete examples for functions, games, calculators, menus, files, JSON, classes, and debugging.

## Changing knowledge

Add or edit `.txt` files in `knowledge/`, then restart the application so the in-memory vector index is rebuilt.
