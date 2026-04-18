import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from sqlalchemy.orm import Session
from sqlalchemy import func
from college_predictor_engine.database.models import College


def get_all_colleges(db: Session):
    return db.query(College).all()


def get_colleges_by_tier(db: Session, tier: str):
    return db.query(College).filter(College.tier == tier).all()


def get_colleges_by_exam(db: Session, exam: str):
    return db.query(College).filter(College.entrance_exam == exam).all()


def get_colleges_by_state(db: Session, state: str):
    return db.query(College).filter(College.state == state).all()


def get_colleges_filtered(db: Session, tier=None, exam=None, state=None):
    query = db.query(College)

    if tier:
        query = query.filter(
            func.lower(College.tier).like(f"%{tier.lower()}%")
        )

    if exam:
        query = query.filter(
            func.lower(College.entrance_exam).like(f"%{exam.lower()}%")
        )

    if state:
        query = query.filter(
            func.lower(College.state).like(f"%{state.lower()}%")
        )

    return query.all()