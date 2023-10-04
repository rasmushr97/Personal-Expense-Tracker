import streamlit as st
from models.expense import Expense
from typing import List
from dataclasses import asdict
import json
import datetime
from json import JSONEncoder
from pydantic import RootModel
import pandas as pd
import numpy as np


class ExpenseManager():
    def __init__(self):
        with open("files/expenses.json", "r") as f:
            try :
                expenses_dict = json.load(f)
            except json.decoder.JSONDecodeError:
                expenses_dict = []
        
        self.expenses = [Expense(**expense) for expense in expenses_dict]
    
    def get_expenses_as_records(self):
        return [RootModel[Expense](expense).model_dump() for expense in self.expenses]
    
    def _update_json(self):
        with open("files/expenses.json", "w") as f:
            objs = self.get_expenses_as_records()
            json.dump(objs, f, cls=DateTimeEncoder)
    
    def add_expense(self, expense: Expense):
        self.expenses.append(expense)
        self._update_json()
    
    def get_expenses(self):
        return self.expenses
    
    def delete_expense(self, expense: Expense):
        self.expenses.remove(expense)
        self._update_json()
        
    def set_expenses(self, expenses: List[Expense]):
        self.expenses = expenses
        self._update_json()


class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()


expense_manager = ExpenseManager()
df = pd.DataFrame.from_records(expense_manager.get_expenses_as_records())
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
df = df.set_index("date")

df["Month"] = df.index.strftime("%Y-%m")
df = df.pivot_table(index="category", columns="Month", values="amount", aggfunc="sum")


st.dataframe(df)