"""
Ad Intelligence Kenya - Main Application Entry Point
"""
import streamlit as st
from auth.auth import init_session, login, logout
from assets.styles import apply_styles
from database.db import init_database
import pages.admin as admin
import pages.client as client

# Initialize database
init_database()

# Initialize session and styles
init_session()
apply_styles()

# Main app routing
if st.session_state.logged_in:
    if st.session_state.role == 'admin':
        admin.render()
    else:
        client.render()
else:
    # Login page
    st.markdown("""
    <div class="app-header">
        <div class="header-title">
            <h1>🎯 Ad Intelligence Kenya</h1>
            <p>Data-driven advertising analytics platform</p>
        </div>
        <div></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <h2>🔐 Welcome Back</h2>
                <p>Sign in to access your advertising intelligence dashboard</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.button("Login", use_container_width=True):
            if login(username, password):
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #E2E8F0;">
            <p style="font-size: 0.75rem; color: #64748B;">Demo Accounts:</p>
            <p style="font-size: 0.7rem; color: #475569;">📊 Admin: <strong>admin</strong> / <strong>admin123</strong></p>
            <p style="font-size: 0.7rem; color: #475569;">🏢 Client: <strong>safaricom</strong> / <strong>client123</strong></p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer"><p>© 2024 Ad Intelligence Kenya | AI-Powered Media Recommendations & Lead Management</p></div>', unsafe_allow_html=True)
