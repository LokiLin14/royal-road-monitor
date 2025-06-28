from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def init_db(engine: create_engine):
    Base.metadata.create_all(bind=engine)
