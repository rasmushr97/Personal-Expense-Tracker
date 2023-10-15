import pandas as pd
from typing import List
from models import MetaModel

def df_from_records(records: List[MetaModel]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    
    df = pd.DataFrame.from_records([dict(record) for record in records])  
    df = df.set_index("id")
    df = df.drop(columns=["created_at", "user_id"])
    df.columns = df.columns.str.capitalize()  
    df["Delete"] = False
    
    return df