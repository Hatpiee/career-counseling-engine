import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load .env (for local development only)
load_dotenv()

# Use DATABASE_URL directly (works for Render)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

# Fix for Render PostgreSQL SSL (important)
if "render.com" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"sslmode": "require"}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()