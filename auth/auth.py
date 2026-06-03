"""
Authentication module - Handles login, logout, and session management
"""
import streamlit as st
from database.db import get_connection

def check_login(username, password):
    """Verify user credentials"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, role, company_id FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result

def init_session():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'company_id' not in st.session_state:
        st.session_state.company_id = None
    if 'recs' not in st.session_state:
        st.session_state.recs = None
    if 'rec_params' not in st.session_state:
        st.session_state.rec_params = {}

def login(username, password):
    """Perform login"""
    user = check_login(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.user_id = user[0]
        st.session_state.username = user[1]
        st.session_state.role = user[2]
        st.session_state.company_id = user[3]
        return True
    return False

def logout():
    """Perform logout"""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.company_id = None
    st.session_state.recs = None
    st.session_state.rec_params = None
