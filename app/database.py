import os
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)

class Base(DeclarativeBase): pass
SessionLocal = sessionmaker(autoflush=False, bind=engine)