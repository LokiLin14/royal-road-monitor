from datetime import datetime
from typing import List, Tuple, Optional

from sqlalchemy import func, and_
from sqlalchemy.orm import aliased

from ..royalroad.models import FictionSnapshot, WatchedURL, NotInterestedInFiction

def all_fictions(db_session, max_entries_returned:int):
    query = db_session.query(
        FictionSnapshot,
    ).order_by(
        FictionSnapshot.snapshot_time.desc(),
        FictionSnapshot.from_ranking.asc()
    ).limit(max_entries_returned)
    return query.all()

# Returns a list of fiction snapshots not in the not_interested table ordered by their first time they were seen
def new_fictions(db_session, max_entries_returned : int=100, from_url : str="") -> list[type[FictionSnapshot]]:
    # Filter for only snapshots in the url and number the snapshots by their creation time
    first_appearances = db_session.query(
        FictionSnapshot.fiction_id,
        func.min(FictionSnapshot.snapshot_time).label('snapshot_time'),
    ).filter(
        FictionSnapshot.from_url == from_url,
        FictionSnapshot.fiction_id.not_in(db_session.query(NotInterestedInFiction.fiction_id))
    ).group_by(
        FictionSnapshot.fiction_id,
    ).subquery()
    first_snapshots = db_session.query(
        FictionSnapshot,
    ).join(
        first_appearances,
        and_(
            FictionSnapshot.fiction_id == first_appearances.c.fiction_id,
            FictionSnapshot.snapshot_time == first_appearances.c.snapshot_time,
        )
    ).order_by(
        FictionSnapshot.snapshot_time.desc(),
        FictionSnapshot.from_ranking.asc()
    ).limit(max_entries_returned)
    return first_snapshots.all()

def dont_show_fictions(db_session, max_entries_returned:int=100) -> List[Tuple[NotInterestedInFiction, FictionSnapshot]]:
    first_appearances = db_session.query(
        FictionSnapshot.fiction_id,
        func.min(FictionSnapshot.snapshot_time).label('snapshot_time'),
    ).group_by(
        FictionSnapshot.fiction_id,
    ).subquery()
    first_snapshots = db_session.query(
        FictionSnapshot,
    ).join(
        first_appearances,
        and_(
            FictionSnapshot.fiction_id == first_appearances.c.fiction_id,
            FictionSnapshot.snapshot_time == first_appearances.c.snapshot_time,
        )
    ).subquery()
    query = db_session.query(
        NotInterestedInFiction,
        aliased(FictionSnapshot, first_snapshots),
    ).join(
        first_snapshots,
        NotInterestedInFiction.fiction_id == first_snapshots.c.fiction_id,
        full=True
    ).filter(
        NotInterestedInFiction.fiction_id.is_not(None)
    ).order_by(
        NotInterestedInFiction.marked_time.desc(),
    ).limit(max_entries_returned)
    return query.all()

def watched_urls(db_session) -> List[type[WatchedURL]]:
    return db_session.query(WatchedURL).all()

def snapshots_of_fiction(db_session, fiction_id, from_url) -> List[FictionSnapshot]:
    query = db_session.query( 
        FictionSnapshot
    ).filter(
        FictionSnapshot.fiction_id == fiction_id,
        FictionSnapshot.from_url == from_url
    ).order_by(
        FictionSnapshot.snapshot_time.asc()
    )
    return query.all()

def latest_snapshot(db_session, fiction_id) -> Optional[FictionSnapshot]:
    snapshots = db_session.query(
        FictionSnapshot
    ).filter(
        FictionSnapshot.fiction_id == fiction_id
    ).order_by(
        FictionSnapshot.snapshot_time.desc()
    ).limit(1).all()
    if len(snapshots) == 0:
        return None
    else:
        return snapshots[0]