import streamlit as st
from models import Expense
import pandas as pd
from resources import SupabaseContextManager
from repositories import CategoryRepository, ExpenseRepository
from utils import df_from_records

VALUTA = "Kr"

class AddExpensePage():
    def __init__(self, category_repository: CategoryRepository, expense_repository: ExpenseRepository):
        self.categories = [category.name for category in category_repository.get_all()]
        
        self.expense_repository = expense_repository
        
    def render(self):
        self.create_expense()            
        self.show_expenses()
        
    def show_expenses(self):
        expenses = self.expense_repository.get_all()
        df = df_from_records(expenses)

        st.divider()
        
        df.insert(3, "Amount Bar", df["Amount"].copy())
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
            indexes = (df != out).any(axis=1)
            changed_rows = out.loc[indexes]
            
            for expense_id, row in changed_rows.iterrows():
                expense_id = str(expense_id)
                
                if row["Delete"]:
                    self.expense_repository.delete(expense_id)
                else: # Update
                    new_expense = Expense(
                        id=expense_id,
                        date=row["Date"],
                        name=row["Name"],
                        amount=row["Amount"],
                        category=row["Category"],
                        description=row["Description"],
                    )
                    self.expense_repository.update(new_expense)
            
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
                expense = Expense(
                    date=date,
                    name=name,
                    amount=amount,
                    category=category,
                    description=description,
                )
                self.expense_repository.add(expense)
    

if __name__ == "__main__":
    with SupabaseContextManager() as context:
        if context.auth_succes:
            page = AddExpensePage(
                context.category_repository,
                context.expense_repository
            )
            page.render()
