import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load database URL from environment variable, with a fallback to your local MySQL database
db_url = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:Subhankar21@localhost:3306/first_jisce_hackthon"
)
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
# Keep session variable for potential compatibility with existing code
session = SessionLocal