# A FictionSnapshot is the state of a fiction at a specific point in time.
from typing import List

from ..database import Base
from sqlalchemy import Column, DateTime, String, Float, Integer, Boolean

class FictionSnapshot(Base):
    __tablename__ = 'fiction_snapshots'
    snapshot_time = Column(DateTime, primary_key=True)
    fiction_id = Column(String, primary_key=True)
    url = Column(String, primary_key=False)
    cover_url = Column(String, primary_key=False)
    title = Column(String, primary_key=False)
    description = Column(String, primary_key=False)
    tags = Column(String, primary_key=False)
    pages = Column(Integer, primary_key=False)
    chapters = Column(Integer, primary_key=False)
    rating = Column(Float, primary_key=False)
    from_url = Column(String, primary_key=True)
    from_ranking = Column(Integer, primary_key=False)

    def __init__(self, snapshot_time, fiction_id, url, cover_url, title, description, tags : List[str], pages, chapters, rating, from_url, from_ranking):
        self.snapshot_time = snapshot_time
        self.fiction_id = fiction_id
        self.url = url
        self.cover_url = cover_url
        self.title = title
        self.description = description
        self.tags = ','.join(tags)
        self.pages = pages
        self.chapters = chapters
        self.rating = rating
        self.from_url = from_url
        self.from_ranking = from_ranking

    def description_paragraphs(self):
        return self.description.split('\n')

    def __repr__(self) -> str:
        return '<FictionSnapshot title=%r, url=%r, id=%r, snapshot_time=%r>' % (self.title, self.url, self.fiction_id, self.snapshot_time)

class NotInterestedInFiction(Base):
    __tablename__ = 'not_interested_in_fictions'
    fiction_id = Column(String, primary_key=True)
    marked_time = Column(DateTime, primary_key=False)

    def __init__(self, fiction_id, marked_time):
        self.fiction_id = fiction_id
        self.marked_time = marked_time

    def __repr__(self) -> str:
        return '<NotInterestedInFiction fiction_id=%r, marked_time=%r>' % (self.fiction_id, self.marked_time)

class WatchedURL(Base):
    __tablename__ = 'watched_urls'
    url = Column(String, primary_key=True)
    active = Column(Boolean, primary_key=False)
    alias = Column(String, primary_key=False)
    def __init__(self, url, active, alias):
        self.url = url
        self.active = active
        self.alias = alias
    def __repr__(self) -> str:
        return '<WatchedURL url=%r, alive=%r, alias=%r>' % (self.url, self.active, self.alias)