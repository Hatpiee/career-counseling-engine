import pandas as pd

from app.database.db_config import SessionLocal
from app.database.models import College


def load_colleges():

    file_path = "data/colleges_fixed.xlsx"

    df = pd.read_excel(file_path)

    print("Excel Columns:")
    print(df.columns)

    session = SessionLocal()

    for _, row in df.iterrows():

        college = College(
            college_id=row["college_id"],
            college_name=row["college_name_y"],   # FIXED COLUMN
            state=row["state"],
            city=row["city"],
            tier=row["tier"],
            institution_type=row["institution_type"],
            entrance_exam=row["entrance_exam"]
        )

        session.add(college)

    session.commit()
    session.close()

    print("Colleges table loaded successfully")


if __name__ == "__main__":
    load_colleges()