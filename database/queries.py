from datetime import datetime
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import aliased

from database import db_session, init_db
from royalroad.models import FictionSnapshot, ViewedFiction

def interested_fictions(amt : int) -> List[FictionSnapshot]:
    # Get interested fictions
    subquery = db_session.query(
        FictionSnapshot,
        func.row_number().over(
            partition_by=FictionSnapshot.url,
            order_by=FictionSnapshot.snapshot_time.desc()
        ).label('rn')
    ).filter(
        FictionSnapshot.url.not_in(
            db_session.query(ViewedFiction.url)
        )
    ).subquery()
    # Get the latest snapshot entry
    fictions = (db_session.query(
        aliased(FictionSnapshot, subquery)
    ).filter(
        subquery.c.rn == 1
    ).order_by(
        subquery.c.snapshot_time.desc()
    ).limit(amt).all())
    return fictions

def add_data():
    snapshot = FictionSnapshot(
        snapshot_time = datetime.now(),
        url = "test0",
        cover_url = "",
        title = "test0",
        description = "",
        tags = "",
        pages = 0,
        chapters = 0,
        rating = 4.5,
        from_url="",
        from_ranking = 0
    )
    db_session.add(snapshot)
    db_session.commit()
    not_interested = ViewedFiction(
        url = "test0",
        marked_time = datetime.now(),
        interested=True
    )
    db_session.add(not_interested)
    db_session.commit()
    pass

if __name__ == '__main__':
    init_db()

    fictions = interested_fictions(20)
    print(fictions)