import os
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DB_PATH = os.environ.get(
    "STAMPD_DB_PATH", os.path.join(os.path.dirname(__file__), "stampd.db")
)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Stamp(Base):
    __tablename__ = "stamps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_path = Column(String)
    stamp_name = Column(String)
    catalog_number = Column(String)
    country = Column(String)
    color = Column(String)
    denomination = Column(String)
    perforation = Column(String)
    format = Column(String)         # Single, Pair, Block
    mint_used = Column(String)      # Mint, Used
    year = Column(String)
    description = Column(String)
    notes = Column(String)
    collection = Column(String)     # Collection/Tag
    listed = Column(String)         # Yes / No
    marketplace = Column(String)    # eBay, Delcampe, etc.
    listing_url = Column(String)
    price = Column(Float)
    sold = Column(String)           # Yes / No
    lot_number = Column(String)
    listing_status = Column(String)  # Unlisted, Draft, Live, Sold
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


def init_db():
    """Initializes the database and creates the table if not exists."""
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
    print("✅ Database initialized at", DB_PATH)
