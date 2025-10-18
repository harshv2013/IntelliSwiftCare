# utils/session_manager.py
import streamlit as st
import uuid

def init_session():
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"user_{uuid.uuid4().hex[:8]}"
    if "chat_id" not in st.session_state:
        st.session_state.chat_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []  # list of dicts: {"role":..., "content":..., "sources": [...]}

def new_chat():
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state.messages = []
