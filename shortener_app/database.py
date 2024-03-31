from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import getSettings

engine = create_engine(
    getSettings().db_url,
    connect_args={"check_same_thread": False}
    # check_same_thread is False to allow multiple requrests to the database at the same time.
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
