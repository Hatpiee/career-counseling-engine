from database.db_config import engine
from database.models import Base

Base.metadata.create_all(bind=engine)

print("Database ORM initialized")