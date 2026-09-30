# 05 — Database Teaching Guide

The teaching edition uses one SQLite table:

```text
users
├── id
├── name
├── email
├── password
└── created_at
```

There is no `username`, `password_hash`, `is_admin`, chat-history table, model table, usage table, credential table, or artifact table.

## Main SQL

- `CREATE TABLE`
- `INSERT`
- `SELECT`
- `UPDATE`
- `DELETE`

## Admin connection

```text
admin.html
  ↓ POST/GET /admin
main.py
  ↓
admin.py
  ↓
database.py
  ↓
SQLite
```

The password column stores a secure hash. A hash is not encrypted plaintext; it is a one-way password representation used for verification.

SQLite documentation: https://www.sqlite.org/docs.html
