import os
from datetime import datetime

import pytest

from sqlalchemy import create_engine, result_tuple
from sqlalchemy.orm import scoped_session, sessionmaker

from ..database import queries 

@pytest.fixture
def init_db_session(): 
    db_dir = os.path.dirname(os.path.abspath(__file__))
    engine = create_engine(f'sqlite:///{db_dir}/test.db')
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    
    yield db_session
    
    db_session.remove()

def test_hello(init_db_session): 
    assert None is None

def test_latest_content(init_db_session):
    result = queries.latest_snapshot(init_db_session, 129587)
    assert result is not None
    assert result.fiction_id == '129587'
    assert result.snapshot_time == datetime(2025, 8, 30, 14, 51, 28, 577223)

# Sandbox to create tests in,
# `cd PROJECT_ROOT` then `python -m src.royal_road_monitor.tests.test_queries`
if __name__ == "__main__": 
    db_dir = os.path.dirname(os.path.abspath(__file__))
    engine = create_engine(f'sqlite:///{db_dir}/test.db')
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    # results = queries.snapshots_of_fiction(db_session, 129587, "https://www.royalroad.com/fictions/rising-stars")
    results = queries.latest_snapshot(db_session, 129587)

    print(results)

    db_session.remove()