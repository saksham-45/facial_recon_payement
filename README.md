# FacePay Prototype (Day 1)

Minimal FastAPI backend scaffolded.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app
```

API at http://localhost:8000

- Health: GET /health
- Users: POST /users, GET /users
- Merchants: POST /merchants, GET /merchants
- Transactions: POST /transactions, GET /transactions?user_id=1

DB: SQLite file `facepay.db` in project root. Tables auto-created on first import once we add `create_all()` in startup (coming next). 