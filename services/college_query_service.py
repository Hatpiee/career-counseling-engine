from sqlalchemy.orm import Session
from database.models import College

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
        query = query.filter(College.tier == tier)

    if exam:
        query = query.filter(College.entrance_exam == exam)

    if state:
        query = query.filter(College.state == state)

    return query.all()