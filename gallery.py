
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from db import Base, Session, Stamp

# Define Tag model and association table if not present
tag_association = Table(
    "stamp_tags",
    Base.metadata,
    Column("stamp_id", Integer, ForeignKey("stamps.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    stamps = relationship(
        "Stamp",
        secondary=tag_association,
        back_populates="tags",
    )


Stamp.tags = relationship(
    "Tag",
    secondary=tag_association,
    back_populates="stamps",
)


def search_stamps(query: str = "", filters: dict | None = None):
    session = Session()
    q = session.query(Stamp)
    if query:
        q = q.filter(
# Import sqlalchemy.sql.expression for safe SQL expression construction
# Import sqlalchemy.orm for Session and Query types
from sqlalchemy.sql.expression import or_
from sqlalchemy.orm import Session, Query

def search_stamps(query: str = "", filters: dict | None = None):
    session = Session()
    q: Query = session.query(Stamp)
    if query:
        q = q.filter(
            or_(
                Stamp.country.ilike("%" + query + "%"),
                Stamp.description.ilike("%" + query + "%")
            )
        )
    if filters and filters.get("tags"):
        q = q.join(Stamp.tags).filter(Tag.name.in_(filters["tags"]))
            | Stamp.description.ilike(f"%{query}%")
        )
    if filters and filters.get("tags"):
        q = q.join(Stamp.tags).filter(Tag.name.in_(filters["tags"]))
def search_stamps(query: str = "", filters: dict | None = None):
    session = Session()
    try:
        q = session.query(Stamp)
        if query:
            q = q.filter(
                Stamp.country.ilike(f"%{query}%")
                | Stamp.description.ilike(f"%{query}%")
            )
        if filters and filters.get("tags"):
            q = q.join(Stamp.tags).filter(Tag.name.in_(filters["tags"]))
        return q.all()
    except Exception as e:
        # TODO: Implement proper error logging
        print(f"An error occurred while searching stamps: {str(e)}")
        return []
    finally:
        session.close()


def add_tag(stamp_id: int, tag_name: str) -> None:


def add_tag(stamp_id: int, tag_name: str) -> None:
    session = Session()
    stamp = session.query(Stamp).get(stamp_id)
    tag = session.query(Tag).filter_by(name=tag_name).first()
    if not tag:
        tag = Tag(name=tag_name)
        session.add(tag)
        session.commit()
    if tag not in stamp.tags:
        stamp.tags.append(tag)
        session.commit()
