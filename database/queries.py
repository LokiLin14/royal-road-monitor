from datetime import datetime
from logging.handlers import WatchedFileHandler
from time import sleep
from typing import List, Tuple

from sqlalchemy import func, and_
from sqlalchemy.orm import aliased

from database import db_session, init_db
from royalroad.models import FictionSnapshot, WatchedURL, NotInterestedInFiction


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

def all_fictions(max_entries_returned:int):
    query = db_session.query(
        FictionSnapshot,
    ).order_by(
        FictionSnapshot.snapshot_time.desc(),
        FictionSnapshot.from_ranking.asc()
    ).limit(max_entries_returned)
    return query.all()

# Returns a list of fiction snapshots not in the not_interested table ordered by their first time they were seen
def new_fictions(max_entries_returned : int, from_url : str="") -> List[FictionSnapshot]:
    # Filter for only snapshots in the url and number the snapshots by their creation time
    first_appearances = (db_session.query(
        FictionSnapshot.url,
        func.max(FictionSnapshot.snapshot_time).label('snapshot_time'),
    ).filter(
        FictionSnapshot.from_url == from_url
    ).group_by(
        FictionSnapshot.url,
    ).subquery())
    first_snapshots = db_session.query(
        FictionSnapshot,
    ).join(
        first_appearances,
        and_(
            FictionSnapshot.url == first_appearances.c.url,
            FictionSnapshot.snapshot_time == first_appearances.c.snapshot_time,
        )
    ).order_by(
        FictionSnapshot.snapshot_time.desc(),
        FictionSnapshot.from_ranking.asc()
    ).limit(max_entries_returned)
    return first_snapshots.all()

def dont_show_fictions(max_entries_returned:int=100) -> List[Tuple[NotInterestedInFiction, FictionSnapshot]]:
    first_appearances = db_session.query(
        FictionSnapshot.url,
        func.max(FictionSnapshot.snapshot_time).label('snapshot_time'),
    ).group_by(
        FictionSnapshot.url,
    ).subquery()
    first_snapshots = db_session.query(
        FictionSnapshot,
    ).join(
        first_appearances,
        and_(
            FictionSnapshot.url == first_appearances.c.url,
            FictionSnapshot.snapshot_time == first_appearances.c.snapshot_time,
        )
    ).subquery()
    query = db_session.query(
        NotInterestedInFiction,
        aliased(FictionSnapshot, first_snapshots),
    ).join(
        first_snapshots,
        NotInterestedInFiction.url == first_snapshots.c.url,
        full=True
    ).filter(
        NotInterestedInFiction.url.is_not(None)
    ).order_by(
        NotInterestedInFiction.marked_time.desc(),
    )
    return query.all()

def add_data():
    db_session.query(FictionSnapshot).delete()
    db_session.query(WatchedURL).delete()
    db_session.query(NotInterestedInFiction).delete()
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

    new_fics = all_fictions(10);
    print(new_fics)

    dont_shows = dont_show_fictions(10)
    print(dont_shows)


