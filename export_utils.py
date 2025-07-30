import pandas as pd
from db import Session, Stamp

def export_csv(path="export.csv"):
    session = Session()
    stamps = session.query(Stamp).all()
    data = [
        {column.name: getattr(s, column.name) for column in Stamp.__table__.columns}
        for s in stamps
    ]
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    return path
