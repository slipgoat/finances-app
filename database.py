from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app_settings import AppSettings

DATABASE_URL = AppSettings().database_url
engine = create_engine(DATABASE_URL, connect_args={"options": "-c timezone=utc"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
