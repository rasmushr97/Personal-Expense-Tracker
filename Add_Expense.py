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

VALUTA = "Kr"

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

if "expenses" not in st.session_state:
    st.session_state.expenses = []

class AddExpensePage():
    def __init__(self, categories: List[str], expense_manager: ExpenseManager):
        self.categories = categories
        self.expense_manager = expense_manager
        
    def render(self):
        self.create_expense()            
        self.show_expenses()
        
    def show_expenses(self):
        table = [RootModel[Expense](expense).model_dump() for expense in self.expense_manager.get_expenses()]
        if not table:
            return
        
        df = pd.DataFrame(table)
        df.columns = df.columns.str.capitalize() 

        st.divider()
        
        df.insert(3, "Amount Bar", df["Amount"].copy())
        df["Delete"] = False
        
        df = df.sort_values(by=["Date"], ascending=False)
        out = st.data_editor(
            df,
            column_config={
                "Date": st.column_config.DateColumn(
                    "Date",
                    format="D. MMM YYYY",
                    step=1,
                ),
                "Amount": st.column_config.NumberColumn(
                    "Amount",
                    help="The amount of money spent",
                    min_value=0,
                    format=f"%d {VALUTA}",
                ),
                "Amount Bar": st.column_config.ProgressColumn(
                    "Bar",
                    help="The amount of money spent",
                    min_value=0,
                    max_value=df["Amount"].max(),
                    format=f" ",
                    width="small",
                ),
                "Category": st.column_config.SelectboxColumn(
                    "Category",
                    help="The category of the expense",
                    width="small",
                    options=self.categories,
                    required=True,
                ),
                "Delete": st.column_config.CheckboxColumn(
                    "Delete",
                    help="Delete this row",
                    default=False,
                )
            }, 
            hide_index=True,
            use_container_width=True
        )
            
        if not out.equals(df):
            out = out[out["Delete"] == False]
            out = out.drop(columns=["Delete", "Amount Bar"])
            out.columns = out.columns.str.lower()
            out = out.dropna(axis=0, how='any')
            
            self.expense_manager.set_expenses([Expense(**expense) for expense in out.to_dict('records')])
            st.rerun()
    
    def create_expense(self):
        with st.form(key='expense_form'):
            name = st.text_input("Enter an Expense")
            
            col1, col2 = st.columns(2)
            amount = col1.number_input("Enter an Amount", value=0, step=100)
            category = col2.selectbox("Select a Category", self.categories, index=0)
            
            date = st.date_input("Enter a Date")
            description = st.text_input("Enter a Description")
            
            submit_pressed = st.form_submit_button(label='Add')
            if submit_pressed:
                expense = Expense(date, name, amount, category, description)
                self.expense_manager.add_expense(expense)
    
if __name__ == "__main__":
    with open("files/categories.json", "r") as f:
        categories = json.load(f)
    
    expense_manager = ExpenseManager()
    AddExpensePage(categories, expense_manager).render()