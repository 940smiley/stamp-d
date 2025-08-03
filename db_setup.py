import os
from db import Base, engine, Session, Stamp

# Ensure DB exists and tables are created
if not os.path.exists("stampd.db"):
    print("⚡ Creating new database: stampd.db")
Base.metadata.create_all(engine)

# Add 2 sample stamps for testing if DB is empty
session = Session()
if session.query(Stamp).count() == 0:
    print("⚡ Adding 2 sample stamps...")

    # Ensure sample image paths exist
    sample_dir = "images"
    os.makedirs(sample_dir, exist_ok=True)

    sample_stamps = [
        Stamp(
            image_path=os.path.join(sample_dir, "sample_stamp_1.jpg"),
            stamp_name="Andrew Jackson 7¢",
            catalog_number="US-1234",
            country="USA",
            color="Brown",
            denomination="7¢",
            perforation="Perf 12",
            format="Single",
            mint_used="Used",
            year="1938",
            description="U.S. President Andrew Jackson definitive stamp",
            notes="Sample data for demo",
            collection="Sample Collection",
            listed="No",
            marketplace="",
            listing_url="",
            price=0.0,
            sold="No",
            lot_number="L0001",
            listing_status="Unlisted",
        ),
        Stamp(
            image_path=os.path.join(sample_dir, "sample_stamp_2.jpg"),
            stamp_name="Germany 1960s Commemorative",
            catalog_number="DE-5678",
            country="Germany",
            color="Red",
            denomination="20pf",
            perforation="Perf 11",
            format="Single",
            mint_used="Mint",
            year="1965",
            description="West Germany commemorative stamp",
            notes="Sample data for demo",
            collection="Sample Collection",
            listed="No",
            marketplace="",
            listing_url="",
            price=0.0,
            sold="No",
            lot_number="L0002",
            listing_status="Unlisted",
        )
    ]

    session.add_all(sample_stamps)
    session.commit()
    print("✅ Sample stamps added!")
else:
    print("✅ Database already has data; no sample stamps added.")
