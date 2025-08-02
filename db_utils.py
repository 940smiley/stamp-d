# db_utils.py — Database schema and setup for Stamp’d

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DB_PATH

Base = declarative_base()

class Stamp(Base):
    __tablename__ = "stamps"

    id = Column(Integer, primary_key=True)
    image_path = Column(String, unique=True)
    thumbnail_path = Column(String)
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

def init_db():
    Base.metadata.create_all(engine)
