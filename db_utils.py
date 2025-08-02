"""Database utilities for Stamp'd.

This module defines the SQLAlchemy model used by the application and
helper functions for common CRUD operations.
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Iterable, List, Dict, Any

from config import DB_PATH

Base = declarative_base()


class Stamp(Base):
    __tablename__ = "stamps"

    id = Column(Integer, primary_key=True)
    image_path = Column(String, unique=True)
    thumbnail_path = Column(String)
    stamp_name = Column(String)
    country = Column(String)
    denomination = Column(String)
    year = Column(String)
    color = Column(String)
    perforation = Column(String)
    block_type = Column(String)  # Single / Pair / Block / Strip
    description = Column(String)
    catalog_number = Column(String)
    mint_used = Column(String)
    lot_number = Column(String)
    listed = Column(String)  # Yes/No
    listing_url = Column(String)
    price = Column(String)


# Create engine and session
engine = create_engine(f"sqlite:///{DB_PATH}")
Session = sessionmaker(bind=engine)


def init_db() -> None:
    Base.metadata.create_all(engine)


def insert_stamp(data: Dict[str, Any]) -> int:
    session = Session()
    stamp = Stamp(**data)
    session.add(stamp)
    session.commit()
    return stamp.id


def insert_many(stamps: Iterable[Dict[str, Any]]) -> None:
    session = Session()
    session.add_all([Stamp(**s) for s in stamps])
    session.commit()


def get_all_stamps() -> List[Stamp]:
    session = Session()
    return session.query(Stamp).all()


def get_stamp(stamp_id: int) -> Stamp | None:
    session = Session()
    return session.query(Stamp).get(stamp_id)


def update_stamp(stamp_id: int, **fields: Any) -> int:
    session = Session()
    stamp = session.query(Stamp).get(stamp_id)
    if not stamp:
        raise ValueError("Stamp not found")
    for key, value in fields.items():
        setattr(stamp, key, value)
    session.commit()
    return stamp_id
