from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://smashuser:123@localhost:5432/smashdb"



engine = create_engine(DATABASE_URL, client_encoding='utf8')

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
