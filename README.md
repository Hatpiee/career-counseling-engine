# Hybrid Career Intelligence and College Recommendation Platform

An AI-powered career intelligence platform that helps students:

* 🎯 Predict suitable colleges based on rank & academic profile
* 💼 Get personalized career recommendations
* 🧭 Receive structured roadmaps and required skills

---

# 🚀 Features

## 🎯 College Predictor

* Uses rank + board percentage
* Categorizes colleges into:

  * Dream
  * Target
  * Safe
* Backed by PostgreSQL dataset

---

## 💼 Career Recommendation (AI-powered)

* Natural language input (user interests)
* AI-based career matching
* Outputs:

  * Match score
  * Skills required
  * Step-by-step roadmap

---

## ⚙️ Full Stack System

| Layer    | Technology |
| -------- | ---------- |
| Frontend | Streamlit  |
| Backend  | FastAPI    |
| Database | PostgreSQL |
| ORM      | SQLAlchemy |
| AI       | Groq + LLM |

---

# 🧩 Project Structure

```
career-counseling-engine/
│
├── college_predictor_engine/
│   ├── app/
│   │   └── database/
│   │       ├── db_config.py
│   │       ├── models.py
│   │       └── init_db.py
│   │
│   ├── services/
│   │   └── college_query_service.py
│   │
│   ├── data/
│   │   └── colleges_master_final_with_cutoff.csv
│
├── services/
│   ├── career_matcher.py
│   ├── profile_extractor.py
│   └── retriever.py
│
├── main_rag.py              # FastAPI backend
├── app.py                   # Streamlit frontend
├── requirements.txt
├── .env
└── README.md
```

---

# ⚙️ Setup Instructions

## 1️⃣ Clone Repository

```bash
git clone <repo-url>
cd career-counseling-engine
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
```

### Activate

**Windows**

```bash
.venv\Scripts\activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Setup Environment Variables

Create a `.env` file in root:

```env
# DATABASE
DB_HOST=localhost
DB_PORT=5432
DB_NAME=career_counseling_db
DB_USER=postgres
DB_PASSWORD=your_password

# API KEYS
GROQ_API_KEY=your_key
GOOGLE_API_KEY=your_key
ASSEMBLYAI_API_KEY=your_key
```

---

## 5️⃣ Setup PostgreSQL

* Open pgAdmin
* Create database:

```
career_counseling_db
```

---

## 6️⃣ Run Backend

```bash
uvicorn main_rag:app --reload --port 8000
```

Check:

```
http://127.0.0.1:8000/docs
```

---

## 7️⃣ Run Frontend

```bash
streamlit run app.py
```

👉 Frontend automatically starts backend if not running

---

# 🔌 API Endpoints

| Endpoint            | Method | Description              |
| ------------------- | ------ | ------------------------ |
| `/predict-college`  | POST   | College prediction       |
| `/chat`             | POST   | Career recommendations   |
| `/transcribe`       | POST   | Audio transcription      |
| `/recommend-career` | POST   | Structured career output |

---

# 🧠 System Architecture

```
User → Streamlit UI
      ↓
FastAPI Backend (main_rag.py)
      ↓
├── College Predictor (PostgreSQL)
├── Career Matcher (LLM)
└── Retriever (RAG pipeline)
```

---

# 🌿 Git Branch Strategy

| Branch       | Purpose                |
| ------------ | ---------------------- |
| main         | Stable production code |
| dev          | Shared development     |
| dev-shreyash | Personal work          |

---

## 🚫 Rules

### ❌ Never push directly to main

```bash
git push origin main
```

---

### ✅ Development Workflow

```bash
git checkout dev
git pull origin dev

git checkout dev-shreyash
```

Work:

```bash
git add .
git commit -m "feature added"
git push origin dev-shreyash
```

Then create PR:

```
dev-shreyash → dev
```

Final merge:

```
dev → main
```

---

# 📦 Current Status

### ✅ Completed

* College Predictor Engine
* Career Recommendation System
* FastAPI Backend
* Streamlit Frontend
* PostgreSQL Integration

---

### 🚧 Future Enhancements

* NLP Query Parser
* Better ranking algorithm
* UI improvements
* Deployment-ready architecture
* Model optimization (memory-safe)

---

# ⚠️ Notes

* Backend runs locally (not deployed)
* Requires PostgreSQL running
* Heavy AI models may not work on low-memory cloud platforms

---

# 👨‍💻 Author

Shreyash Tripathy
Hybrid Career Intelligence and College Recommendation Platform

---

# ⭐ If you like this project

Give it a star ⭐ on GitHub
