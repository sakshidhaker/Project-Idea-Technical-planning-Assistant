# 14 — Python Generation Guide

## Why this version focuses on Python

The Teaching Edition is intentionally small. General Chat can discuss many technical topics, but the reliable programming-generation path is deliberately focused on Python. This avoids adding language routers, multiple validators, and separate code-generation systems before students need them.

## What happens when a student asks for Python code

```text
Student request
      ↓
RAG semantic search
      ↓
Python examples and documentation
      ↓
Qwen prompt with Python rules
      ↓
Generated Python code
      ↓
Small validator
      ↓
One retry if needed
      ↓
PDF / DOCX
```

## Common requests

The knowledge base includes complete examples for functions, games, calculators, menu programs, file tools, JSON, classes, and debugging. Students can ask natural-language requests such as:

```text
Create a Python function that adds two numbers.

Create a Python Rock Paper Scissors game.

Write Python code to save a dictionary to JSON.

Create a Python calculator with +, -, *, and /.
```

These are examples of request types, not hardcoded questions.

## Why the knowledge base was expanded

A small local model is more reliable when retrieval gives it complete and correct patterns instead of only isolated definitions. The added files therefore contain complete Python snippets and generation checklists.

## Current limitation

Python is the programming language whose generated code this edition is designed to validate. Other languages remain useful in Chat for explanations, but their program-generation correctness is not guaranteed in this version.
