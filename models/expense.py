from pydantic.dataclasses import dataclass
from datetime import date

@dataclass
class Expense:
    date: date
    name: str
    amount: float
    category: str
    description: str
