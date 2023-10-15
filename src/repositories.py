from supabase.client import Client
import pandas as pd
from models import Expense, Category, MetaModel
from pydantic import TypeAdapter, BaseModel
from typing import List
from abc import ABC, abstractmethod


class BaseRepository(ABC):
    def __init__(self, client : Client, user_id: str, table_name: str) -> None:
        self.client = client
        self.user_id = user_id
        self.table_name = table_name
    
    @abstractmethod
    def parse_response(self, response) -> List[MetaModel]:
        pass
    
    def get_all(self) -> List[MetaModel]:
        query = (
            self.client
            .table(self.table_name)
            .select("*")
            .eq("user_id", self.user_id)
        )
        repsonse = query.execute()
        return self.parse_response(repsonse)

    def add(self, item: BaseModel) -> List[MetaModel]:
        data_dict = item.model_dump()
        data_dict = {k: v for k, v in data_dict.items() if v is not None}
        data_dict["user_id"] = self.user_id
        query = (
            self.client
            .table(self.table_name)
            .insert(data_dict)
        )
        repsonse = query.execute()
        return self.parse_response(repsonse)

    def delete(self, item_id: str) -> List[MetaModel]:
        query = (
            self.client
            .table(self.table_name)
            .delete()
            .eq("id", item_id)
        )
        repsonse = query.execute()
        return self.parse_response(repsonse)
    
    def update(self, item: MetaModel) -> List[MetaModel]:
        item_id = item.id
        data_dict = item.model_dump()
        data_dict = {k: v for k, v in data_dict.items() if v is not None}
        query = (
            self.client
            .table(self.table_name)
            .update(data_dict)
            .eq("id", item_id)
        )
        repsonse = query.execute()
        return self.parse_response(repsonse)

class ExpenseRepository(BaseRepository):
    def __init__(self, client : Client, user_id: str) -> None:
        super().__init__(client, user_id, "Expenses")
    
    def parse_response(self, response) -> List[Expense]:
        data = response.data
        ta = TypeAdapter(List[Expense])
        expenses = ta.validate_python(data)
        return expenses


class CategoryRepository(BaseRepository):
    def __init__(self, client : Client, user_id: str) -> None:
        super().__init__(client, user_id, "Categories")
    
    def parse_response(self, response) -> List[Category]:
        data = response.data
        ta = TypeAdapter(List[Category])
        categories = ta.validate_python(data)
        return categories
    
    
    

    