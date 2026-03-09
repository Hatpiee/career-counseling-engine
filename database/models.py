from sqlalchemy import Column, String
from database.db_config import Base

class College(Base):
    __tablename__ = "colleges"

    college_id = Column(String, primary_key=True, index=True)
    college_name = Column(String)
    state = Column(String)
    city = Column(String)
    tier = Column(String)
    institution_type = Column(String)
    entrance_exam = Column(String)