"""
Admin Dashboard Page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import get_all_companies, get_available_years
from services.bookings import get_bookings, update_booking_status, get_booking_statistics
from services.leads import get_leads, update_lead_status, get_lead_statistics
from services.stations import get_all_stations
from assets.styles import apply_styles
from utils.helpers import format_currency, format_date

def render():
    apply_styles()
    
    # Header with gradient background
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown("""
        <div class="app-header">
            <div class="header-title">
                <h1>📊 Admin Dashboard</h1>
                <p>Complete overview of all advertising activities</p>
            </div>
            <div></div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Time filter
    available_years = get_available_years()
    months = ["All Months", "January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("📅 Select Year", options=available_years, index=0 if available_years else 0)
    with col2:
        selected_month_name = st.selectbox("📆 Select Month", options=months)
        selected_month = None if selected_month_name == "All Months" else months.index(selected_month_name)
    
    # Get data
    all_companies = get_all_companies()
    all_bookings = get_bookings(year=selected_year, month=selected_month)
    all_leads = get_leads(year=selected_year, month=selected_month)
    booking_stats = get_booking_statistics(year=selected_year, month=selected_month)
    lead_stats = get_lead_statistics(year=selected_year, month=selected_month)
    
    # Statistics Row
    cols = st.columns(5)
    metrics = [
        ("🏢 Companies", len(all_companies)),
        ("📋 Bookings", booking_stats["total"]),
        ("⏳ Pending", booking_stats["pending_approval"]),
        ("✅ Confirmed", booking_stats["confirmed"]),
        ("👥 Leads", lead_stats["total"])
    ]
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Pending Approvals", "👥 All Leads", "📺 Media Directory", "🏢 Companies"])
    
    # Tab 1: Pending Approvals
    with tab1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Pending Approval Requests</p>', unsafe_allow_html=True)
        
        pending_bookings = all_bookings[all_bookings['status'] == 'pending_approval'] if not all_bookings.empty else pd.DataFrame()
        if not pending_bookings.empty:
            for _, b in pending_bookings.iterrows():
                st.markdown(f"""
                <div class="booking-card booking-card-pending">
                    <div class="booking-header">
                        <span class="booking-id">Booking #{b['booking_id']}</span>
                        <span class="booking-date">{format_date(b['request_date'])}</span>
                    </div>
                    <div class="booking-details">
                        <div><span class="booking-detail-label">Company:</span> {b.get('company_name', 'N/A')}</div>
                        <div><span class="booking-detail-label">Stations:</span> {b.get('selected_stations', b['station_name'])}</div>
                        <div><span class="booking-detail-label">Budget:</span> {format_currency(b['budget_kes'])}</div>
                        <div><span class="booking-detail-label">Duration:</span> {b['duration_days']} days</div>
                        <div><span class="booking-detail-label">Contact:</span> {b['contact_name']}</div>
                        <div><span class="booking-detail-label">Email:</span> {b['contact_email']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    notes = st.text_area("Admin Notes", key=f"notes_{b['booking_id']}", placeholder="Add notes...")
                with col2:
                    if st.button(f"✅ Approve", key=f"approve_{b['booking_id']}"):
                        update_booking_status(b['booking_id'], 'approved', notes)
                        st.success(f"Booking #{b['booking_id']} approved!")
                        st.rerun()
                    if st.button(f"❌ Suspend", key=f"suspend_{b['booking_id']}"):
                        update_booking_status(b['booking_id'], 'suspended', notes)
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No pending approvals")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 2: All Leads
    with tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">All Audience Leads</p>', unsafe_allow_html=True)
        
        if not all_leads.empty:
            cols = st.columns(4)
            lead_metrics = [
                ("📊 Total", lead_stats["total"]),
                ("🆕 New", lead_stats["new"]),
                ("✅ Converted", lead_stats["converted"]),
                ("📈 Conv. Rate", f"{lead_stats['conversion_rate']}%")
            ]
            for col, (label, value) in zip(cols, lead_metrics):
                with col:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)
            st.markdown("---")
            
            for _, lead in all_leads.iterrows():
                status_badge = '<span class="badge-new">NEW</span>' if lead['status'] == 'new' else '<span class="badge-contacted">CONTACTED</span>' if lead['status'] == 'contacted' else '<span class="badge-converted">CONVERTED</span>'
                st.markdown(f"""
                <div class="lead-card">
                    <div class="lead-header">
                        <strong>{lead['lead_name']}</strong>
                        <span>{status_badge}</span>
                    </div>
                    <div class="lead-contact">
                        <span>📞 {lead['lead_phone']}</span>
                        <span>📧 {lead['lead_email']}</span>
                        <span>🏢 {lead.get('company_name', 'N/A')}</span>
                    </div>
                    <div><strong>Interest:</strong> {lead['interest_product']}</div>
                    <div class="lead-message"><strong>Message:</strong> {lead['message'][:150] if lead['message'] else 'No message'}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if lead['status'] == 'new':
                    if st.button(f"📞 Mark Contacted", key=f"contact_{lead['lead_id']}"):
                        update_lead_status(lead['lead_id'], 'contacted')
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No leads found for selected period")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 3: Media Directory
    with tab3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Media Directory with Contacts</p>', unsafe_allow_html=True)
        
        region_filter = st.selectbox("Filter by Region", ["All", "National", "Coast", "Western", "Central"])
        
        for station in get_all_stations():
            if region_filter == "All" or station['region'] == region_filter:
                with st.expander(f"📺 {station['name']} ({station['media_type']}) - {station['region']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Reach:** {station['reach']:,}")
                        st.write(f"**Price Tier:** {station['price_tier']}")
                    if station['contacts']:
                        with col2:
                            st.write("**Contact Information:**")
                            st.write(f"👤 {station['contacts']['contact_person']}")
                            st.write(f"📞 {station['contacts']['contact_phone']}")
                            st.write(f"📧 {station['contacts']['contact_email']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 4: Companies
    with tab4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Registered Companies</p>', unsafe_allow_html=True)
        if not all_companies.empty:
            st.dataframe(all_companies, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
