from datetime import datetime
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import aliased

from database import db_session, init_db
from royalroad.models import FictionSnapshot, ViewedFiction

def unviewed_fictions(max_entries_returned : int) -> List[FictionSnapshot]:
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
        subquery.c.from_ranking.asc()
    ).limit(max_entries_returned).all())
    return fictions

def followed_fictions(max_entries_returned : int) -> List[FictionSnapshot]:
    subquery = db_session.query(
        FictionSnapshot,
        func.row_number().over(
            partition_by=FictionSnapshot.url,
            order_by=FictionSnapshot.snapshot_time.desc()
        ).label('rn')
    ).filter(
        FictionSnapshot.url.in_(
            db_session.query(
                ViewedFiction.url
            ).filter(
                ViewedFiction.interested.is_(True),
            )
        )
    ).subquery()
    fictions = db_session.query(
        aliased(FictionSnapshot, subquery)
    ).filter(
        subquery.c.rn == 1
    ).order_by(
        subquery.c.from_ranking.asc()
    ).limit(max_entries_returned).all()
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

    fictions = unviewed_fictions(20)
    print(fictions)