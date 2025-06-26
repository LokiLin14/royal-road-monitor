from datetime import datetime
from logging.handlers import WatchedFileHandler
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import aliased

from database import db_session, init_db
from royalroad.models import FictionSnapshot, ViewedFiction, WatchedURL, NotInterestedInFiction


def unviewed_fictions(max_entries_returned : int, from_url="") -> List[FictionSnapshot]:
    # Get interested fictions
    subquery = (db_session.query(
        FictionSnapshot,
        func.row_number().over(
            partition_by=FictionSnapshot.url,
            order_by=FictionSnapshot.snapshot_time.desc()
        ).label('rn')
    ).filter(
        FictionSnapshot.from_url == from_url
    ).filter(
        FictionSnapshot.url.not_in(
            db_session.query(ViewedFiction.url)
        )
    ).subquery())
    # Get the latest snapshot entry
    fictions = (db_session.query(
        aliased(FictionSnapshot, subquery)
    ).filter(
        subquery.c.rn == 1
    ).order_by(
        subquery.c.snapshot_time.desc(),
        subquery.c.from_ranking.asc()
    ).limit(max_entries_returned).all())
    return fictions

# Returns a list of fiction snapshots not in the not_interested table ordered by their first time they were seen
def new_fictions(max_entries_returned : int, from_url : str="") -> List[FictionSnapshot]:
    # Filter for only snapshots in the url and number the snapshots by their creation time
    numbered_snapshots = db_session.query(
        FictionSnapshot,
        func.row_number().over(
            partition_by=FictionSnapshot.url,
            order_by=FictionSnapshot.snapshot_time.asc()
        ).label('rn')
    ).filter(
        FictionSnapshot.from_url == from_url,
        FictionSnapshot.url.not_in(
            db_session.query(NotInterestedInFiction.url)
        )
    ).subquery()
    # Get the latest snapshot entry
    fictions_query = db_session.query(
        aliased(FictionSnapshot, numbered_snapshots)
    ).filter(
        numbered_snapshots.c.rn == 1,
    ).order_by(
        numbered_snapshots.c.snapshot_time.desc(),
        numbered_snapshots.c.from_ranking.asc()
    ).limit(max_entries_returned)
    return fictions_query.all()

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
    snapshot1 = FictionSnapshot(
        snapshot_time=datetime.now(),
        url="test1",
        cover_url="",
        title="test1",
        description="",
        tags="",
        pages=0,
        chapters=0,
        rating=4.5,
        from_url="",
        from_ranking=0
    )
    snapshot2 = FictionSnapshot(
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
    db_session.add(snapshot1)
    db_session.add(snapshot2)
    viewed = ViewedFiction(
        url = "test0",
        marked_time = datetime.now(),
        interested=True
    )
    db_session.add(viewed)
    not_interested = NotInterestedInFiction(
        url = "test0",
        marked_time = datetime.now(),
    )
    db_session.add(not_interested)
    db_session.commit()

def watched_urls() -> List[WatchedURL]:
    return db_session.query(WatchedURL).all()

if __name__ == '__main__':
    init_db()

    add_data()

    new_fics = new_fictions(10, "");

    print(new_fics)