#from pydantic.dataclasses import dataclass
from pydantic import BaseModel, field_serializer
from datetime import date, datetime
from typing import Optional

class MetaModel(BaseModel):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    user_id: Optional[str] = None


class Category(MetaModel):
    name: str

class Expense(MetaModel):
    date: date
    name: str
    amount: float
    category: str
    description: str
    
    @field_serializer('date')
    def serialize_dt(self, date, _):
        return date.strftime("%Y-%m-%d")
