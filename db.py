import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DB_NAME = "stampd.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Stamp(Base):
    __tablename__ = "stamps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_path = Column(String)
    file_hash = Column(String, index=True)  # MD5 hash for duplicate detection
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
    listing_status = Column(String) # Unlisted, Draft, Live, Sold
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db():
    """Initializes the database and creates the table if not exists."""
    Base.metadata.create_all(engine)

def populate_missing_hashes():
    """Populate file_hash for existing records that don't have it."""
    from image_utils import get_file_hash
    session = Session()
    try:
        stamps_without_hash = session.query(Stamp).filter(Stamp.file_hash.is_(None)).all()
        for stamp in stamps_without_hash:
            if stamp.image_path and os.path.exists(stamp.image_path):
                stamp.file_hash = get_file_hash(stamp.image_path)
        session.commit()
        print(f"✅ Updated {len(stamps_without_hash)} stamps with file hashes")
    except Exception as e:
        session.rollback()
        print(f"❌ Error populating hashes: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    init_db()
    populate_missing_hashes()
    print("✅ Database initialized at", DB_PATH)
