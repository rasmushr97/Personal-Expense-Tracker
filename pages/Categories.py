import streamlit as st
import json
from typing import List
import pandas as pd

class CategoryManager():
    CATEGORIES_FILE = "files/categories.json"
    
    def __init__(self):
        with open(CategoryManager.CATEGORIES_FILE, "r") as f:
            try :
                self.categories = json.load(f)
            except json.decoder.JSONDecodeError:
                self.categories = []
                
    def get_categories(self):
        return self.categories
    
    def _update_json(self):
        with open(CategoryManager.CATEGORIES_FILE, "w") as f:
            objs = self.get_categories()
            json.dump(objs, f)
    
    def add_category(self, category: str):
        self.categories.append(category)
        self._update_json()
    
    def delete_category(self, category: str):
        self.categories.remove(category)
        self._update_json()
        
    def set_categories(self, categories: List[str]):
        self.categories = categories
        self._update_json()


class CategoriesPage():
    def __init__(self, category_manager: CategoryManager) -> None:
        self.category_manager = category_manager
    
    def run(self):
        self.create_category()
        self.show_categories()
        
    def create_category(self):
        st.header("Create Category")
        category = st.text_input("Category")
        if st.button("Create Category"):
            self.category_manager.add_category(category)
                           
    def show_categories(self):
        st.divider()
                
        categories = self.category_manager.get_categories()
        if not categories:
            st.text("No categories created yet")
            return
        
    
        table = pd.DataFrame({"Category": categories, "Delete": [False] * len(categories)})
        out = st.data_editor(
            table, 
            column_config={
                "Category": st.column_config.TextColumn(
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
        
        if not out.equals(table):
            out = out[out["Delete"] == False]
            out = out.dropna(axis=0, how='any')
            new_categories = out["Category"].tolist()
            
            self.category_manager.set_categories(new_categories)
            
            st.rerun()
            
            
 
if __name__ == "__main__":
    category_manager = CategoryManager()
    
    page = CategoriesPage(category_manager)
    page.run()