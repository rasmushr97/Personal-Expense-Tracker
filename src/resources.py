import streamlit as st
from supabase.client import create_client, Client
from supabase.lib.client_options import ClientOptions
from repositories import ExpenseRepository, CategoryRepository
from streamlit_supabase_auth import login_form, logout_button
from typing import Tuple
import os


class SupabaseContextManager:
    def __enter__(self):
        url, key = get_supabase_creds()

        self.session = login_form(url=url, apiKey=key)
        self.auth_succes = self.session is not None

        if self.auth_succes:
            self.user_id = self.session["user"]["id"]
            self.client = get_supabase_client(url, key)
            self.expense_repository = ExpenseRepository(self.client, self.user_id)
            self.category_repository = CategoryRepository(self.client, self.user_id)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        with st.sidebar:
            logout_button()


@st.cache_resource()
def get_supabase_creds() -> Tuple[str, str]:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    return str(url), str(key)

@st.cache_resource()
def get_supabase_client(url: str, key: str) -> Client:
    return create_client(
        url, 
        key, 
        options=ClientOptions(
            postgrest_client_timeout=10, 
        )
    )
   