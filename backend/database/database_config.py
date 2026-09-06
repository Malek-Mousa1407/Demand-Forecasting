from sqlalchemy import create_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", default="postgresql://postgres:postgres@localhost:5432/mydb")
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()