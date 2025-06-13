# A FictionSnapshot is the state of a fiction at a specific point in time.
from database import Base
from sqlalchemy import Column, DateTime, String, Float, Integer, Boolean

class FictionSnapshot(Base):
    __tablename__ = 'fiction_snapshots'
    snapshot_time = Column(DateTime, primary_key=True)
    url = Column(String, primary_key=True)
    cover_url = Column(String, primary_key=False)
    title = Column(String, primary_key=False)
    description = Column(String, primary_key=False)
    tags = Column(String, primary_key=False)
    pages = Column(Integer, primary_key=False)
    chapters = Column(Integer, primary_key=False)
    rating = Column(Float, primary_key=False)
    from_url = Column(String, primary_key=True)
    from_ranking = Column(Integer, primary_key=False)

    def __init__(self, snapshot_time, url, cover_url, title, description, tags, pages, chapters, rating, from_url, from_ranking):
        self.snapshot_time = snapshot_time
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
        return self.description.split('\n\n')

    def __repr__(self) -> str:
        return '<FictionSnapshot title=%r, snapshot_time=%r>' % (self.title, self.snapshot_time)

class ViewedFiction(Base):
    __tablename__ = 'viewed_fictions'
    url = Column(String, primary_key=True)
    marked_time = Column(DateTime, primary_key=True)
    interested = Column(Boolean, primary_key=False)

    def __init__(self, url, marked_time, interested):
        self.url = url
        self.marked_time = marked_time
        self.interested = interested

    def __repr__(self) -> str:
        return '<NotInterestedInFiction url=%r, marked_time=%r, interested=%r>' % (self.url, self.marked_time,
                                                                                   self.interested)