from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql+psycopg2://postgres:NewPassword123!@localhost/stampd"
Base = declarative_base()

class Stamp(Base):
    __tablename__ = "stamps"
    id = Column(Integer, primary_key=True)
    country = Column(String(100))
    denomination = Column(String(50))
    year = Column(String(20))
    notes = Column(Text)
    image_path = Column(Text)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
print("Database tables created successfully!")
