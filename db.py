from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
from datetime import datetime

DATABASE_URL = "sqlite:///stampd.db"
Base = declarative_base()

# Tags (many-to-many)
stamp_tag = Table('stamp_tag', Base.metadata,
    Column('stamp_id', ForeignKey('stamps.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)

class Stamp(Base):
    __tablename__ = "stamps"
    id = Column(Integer, primary_key=True)
    country = Column(String(100))
    denomination = Column(String(50))
    year = Column(String(20))
    notes = Column(Text)
    description = Column(Text)
    image_path = Column(Text)
    condition = Column(String(50))
    collection = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)

    tags = relationship("Tag", secondary=stamp_tag, back_populates="stamps")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    stamps = relationship("Stamp", secondary=stamp_tag, back_populates="tags")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)

SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)  # Shared session
