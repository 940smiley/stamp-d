from config import *
from db import Session, Stamp, Tag

def search_stamps(query="", filters={}):
    session = Session()
    q = session.query(Stamp)
    if query:
        q = q.filter(Stamp.country.ilike(f"%{query}%") | Stamp.notes.ilike(f"%{query}%"))
    if filters.get("tags"):
        q = q.join(Stamp.tags).filter(Tag.name.in_(filters["tags"]))
    return q.all()

def add_tag(stamp_id, tag_name):
    session = Session()
    stamp = session.query(Stamp).get(stamp_id)
    tag = session.query(Tag).filter_by(name=tag_name).first() or Tag(name=tag_name)
    stamp.tags.append(tag)
    session.commit()
