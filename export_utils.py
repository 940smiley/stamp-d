import pandas as pd
from db import Session, Stamp

def export_csv(path="export.csv"):
    session = Session()
    stamps = session.query(Stamp).all()
    data = [s.__dict__ for s in stamps]
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    return path
