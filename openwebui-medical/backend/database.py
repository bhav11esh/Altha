import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from models import Base

SCHEMA = "openwebui"

engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
    connect_args={"options": f"-csearch_path={SCHEMA}"},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def init_db():
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}"))
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
