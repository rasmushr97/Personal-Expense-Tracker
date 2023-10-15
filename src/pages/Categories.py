import streamlit as st
import pandas as pd
from resources import SupabaseContextManager
from repositories import CategoryRepository
from models import Category
from utils import df_from_records

class CategoriesPage():
    def __init__(self, category_repo: CategoryRepository) -> None:
        self.category_repo = category_repo
    
    def render(self):
        self.create_category()
        self.show_categories()
        
    def create_category(self):
        st.header("Create Category")
        category = st.text_input("Category")
        if st.button("Create Category"):
            new_category = Category(name=category)
            self.category_repo.add(new_category)
                           
    def show_categories(self):
        st.divider()
                
        categories = self.category_repo.get_all()
        df = df_from_records(categories)
        df = df.sort_values(by=["Name"])
        
        out = st.data_editor(
            df, 
            column_config={
                "Name": st.column_config.TextColumn(
                    "Category",
                    width="large",
                    help="Category name",
                ),
                "Delete": st.column_config.CheckboxColumn(
                    "Delete",
                    width="small",
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
            
            for category_id, row in changed_rows.iterrows():
                category_id = str(category_id)
                
                if row["Delete"]:
                    self.category_repo.delete(category_id)
                else: # Update
                    new_category = Category(
                        id=category_id,
                        name=row["Name"],
                    )
                    self.category_repo.update(new_category)
            
            st.rerun()
            
            
 
if __name__ == "__main__":
    with SupabaseContextManager() as context:
        if context.auth_succes:
            page = CategoriesPage(
                context.category_repository,
            )
            page.render()