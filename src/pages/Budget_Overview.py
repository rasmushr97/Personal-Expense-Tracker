import streamlit as st
from resources import SupabaseContextManager
from utils import df_from_records
import pandas as pd

class BudgetOverviewPage():
    def __init__(self, expense_repository) -> None:
        self.expense_repository = expense_repository
        
    def render(self):
        expenses = self.expense_repository.get_all()
        df = df_from_records(expenses)
        
        print(df)
        
        df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
        df = df.set_index("Date")
        
        df["Month"] = df.index.strftime("%Y-%m")
        df = df.pivot_table(index="Category", columns="Month", values="Amount", aggfunc="sum")
        
        st.dataframe(df)


if __name__ == "__main__":
    with SupabaseContextManager() as context:
        if context.auth_succes:
            page = BudgetOverviewPage(
                context.expense_repository,
            )
            page.render()