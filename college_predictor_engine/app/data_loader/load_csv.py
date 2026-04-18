import pandas as pd
from college_predictor_engine.app.database.db_config import SessionLocal, engine
from college_predictor_engine.app.database.models import College, Base

def load_colleges():
    file_path = "colleges_master_final_with_cutoff.csv"

    df = pd.read_csv(file_path)

    # 🔥 CREATE TABLE
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    for _, row in df.iterrows():
        college = College(
            college_id=row["college_id"],
            college_name=row["college_name"],
            state=row["state"],
            city=row["city"],
            tier=row["tier"],
            institution_type=row["institution_type"],
            entrance_exam=row["entrance_exam"],
            cutoff=int(row["cutoff"])
        )
        session.add(college)

    session.commit()
    session.close()

    print("✅ Data loaded successfully")

if __name__ == "__main__":
    load_colleges()