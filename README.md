# Career Counseling Engine

Backend system for an AI-powered career counseling platform that recommends colleges and generates personalized career roadmaps.

Currently this repository contains the **data layer**, including PostgreSQL integration, ORM models, and query services.

---

# Project Structure

```id="f4d9xg"
career-counseling-engine
│
├── database
│   ├── db_config.py        # Database connection setup
│   ├── models.py           # SQLAlchemy ORM models
│   └── init_db.py          # Database initialization
│
├── services
│   └── college_query_service.py   # Query layer
│
├── data
│   └── colleges_master_final.csv  # Dataset
│
├── scripts                 # Data preparation scripts
│
├── main.py                 # Backend entry point (future API layer)
├── requirements.txt        # Python dependencies
├── .gitignore
└── README.md
```

---

# Setup Instructions

Clone the repository:

```id="3k6k5o"
git clone <repo-url>
cd career-counseling-engine
```

Create a virtual environment:

```id="tr4y0p"
python -m venv .venv
```

Activate the environment:

Windows:

```id="z8xw7v"
.venv\Scripts\activate
```

Install dependencies:

```id="p7wzde"
pip install -r requirements.txt
```

Create a `.env` file in the root directory:

```id="y4qk2t"
DB_HOST=localhost
DB_PORT=5432
DB_NAME=career_counseling_db
DB_USER=postgres
DB_PASSWORD=your_password
```

---

# Git Branch Structure

The repository uses a **very simple branching system**.

```id="l6z3hk"
main
dev
dev-shreyash
```

### Branch Purpose

```id="q2e1sm"
main  → Stable production-ready code
dev   → Shared development branch
dev-shreyash → Personal development branch
```

---

# IMPORTANT RULES (READ BEFORE PUSHING CODE)

### Rule 1 — NEVER push directly to `main`

`main` must always remain clean and stable.

Do **not** run:

```id="fpx4bg"
git push origin main
```

---

### Rule 2 — First create or switch to your development branch

Before starting work, move to the development branch.

```id="3zgrj3"
git checkout dev
git pull origin dev
git checkout dev-shreyash
```

All work must be done inside:

```id="2rqgex"
dev-shreyash
```

---

### Rule 3 — Do your work and commit normally

Example workflow:

```id="n9x2jv"
git add .
git commit -m "add new feature"
git push origin dev-shreyash
```

---

### Rule 4 — Create a Pull Request

After pushing your changes, open GitHub and create a **Pull Request**.

```id="o3m2ti"
dev-shreyash → dev
```

This merges your work into the shared development branch.

---

### Rule 5 — Only merge dev → main when stable

When the project is stable and tested, merge:

```id="n1s0qk"
dev → main
```

This keeps the `main` branch clean.

---

# Development Flow

```id="c4spjz"
dev-shreyash
        ↓
       dev
        ↓
       main
```

---

# Current Completed Module

The **data layer** is implemented.

It includes:

* PostgreSQL database connection
* SQLAlchemy ORM models
* College query service

Main file:

```id="b17rqh"
services/college_query_service.py
```

Example usage:

```id="4n7yep"
from database.db_config import SessionLocal
from services.college_query_service import get_all_colleges

db = SessionLocal()
colleges = get_all_colleges(db)
```

---

# Next Modules

Planned components:

* College Predictor Engine
* NLP Query Parser
* FastAPI API Layer
* Career Roadmap Generator
