"""
Client Portal Page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import get_company_by_id, get_company_data, get_available_years
from services.bookings import create_booking, get_bookings, update_booking_status, get_booking_statistics
from services.leads import add_lead, get_leads, update_lead_status, get_lead_statistics
from services.recommendations import MediaRecommendationEngine, StationDatabase
from services.stations import get_all_stations
from assets.styles import apply_styles
from utils.helpers import format_currency, format_date, get_month_name

def render():
    apply_styles()
    
    company = get_company_by_id(st.session_state.company_id)
    company_name = company['name'] if company else "Your Company"
    company_email = company['email'] if company else ""
    
    # Header with logout
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"""
        <div class="header-title">
            <h1>👋 Welcome, {company_name}</h1>
            <p>Your personalized advertising intelligence dashboard</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    
    # Time filter
    available_years = get_available_years(st.session_state.company_id)
    months = ["All Months", "January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("📅 Select Year", options=available_years, index=0 if available_years else 0)
    with col2:
        selected_month_name = st.selectbox("📆 Select Month", options=months)
        selected_month = None if selected_month_name == "All Months" else months.index(selected_month_name)
    
    # Get statistics
    lead_stats = get_lead_statistics(st.session_state.company_id, selected_year, selected_month)
    booking_stats = get_booking_statistics(st.session_state.company_id, selected_year, selected_month)
    
    # Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">👥 Total Leads</div><div class="metric-value">{lead_stats["total"]}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">🆕 New Leads</div><div class="metric-value">{lead_stats["new"]}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">✅ Converted</div><div class="metric-value">{lead_stats["converted"]}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">📋 Bookings</div><div class="metric-value">{booking_stats["total"]}</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card"><div class="metric-label">📈 Conv. Rate</div><div class="metric-value">{lead_stats["conversion_rate"]}%</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Recommendations", "📋 My Bookings", "👥 My Leads", "📺 Media Directory", "📊 Performance"])
    
    # Tab 1: Recommendations
    with tab1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">🎯 AI-Powered Media Recommendation Engine</p>', unsafe_allow_html=True)
        
        engine = MediaRecommendationEngine()
        station_db = StationDatabase()
        
        col1, col2 = st.columns(2)
        with col1:
            campaign_goal = st.selectbox("Campaign Goal", ["Brand Awareness", "Lead Generation", "Sales"])
            budget = st.number_input("Budget (KES)", 100000, 10000000, 500000, 50000)
            duration = st.select_slider("Duration (Days)", [7, 14, 21, 30], 14)
        with col2:
            target_audience = st.selectbox("Target Audience", ["Mass Market", "Youth (18-35)", "Professionals"])
            region_type = st.selectbox("Region Type", ["National", "Local", "Both"])
        
        if st.button("🔍 Generate Recommendations", use_container_width=True):
            recs = engine.recommend_stations(campaign_goal, budget, duration, target_audience, region_type)
            st.session_state.recs = recs
            st.session_state.rec_params = {'goal': campaign_goal, 'budget': budget, 'duration': duration, 'audience': target_audience, 'region': region_type}
            st.rerun()
        
        if st.session_state.get('recs'):
            st.markdown("---")
            st.markdown("### 🏆 Recommended Stations")
            for i, r in enumerate(st.session_state.recs[:3]):
                price_icon = "🟢" if r['price_tier'] == "Economy" else "🟡" if r['price_tier'] == "Standard" else "🔴"
                st.markdown(f"""
                <div class="rec-card">
                    <h4>#{i+1} {r['station_name']} ({r['media_type']}) {price_icon} {r['price_tier']}</h4>
                    <p>📊 Reach: {r['reach']:,} | 💰 Cost per spot: {format_currency(r['cost_per_spot'])}</p>
                    <p>📺 Recommended spots: {r['recommended_spots']} per day</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 📞 Book Your Campaign")
            station_options = [f"{r['station_name']} ({r['media_type']})" for r in st.session_state.recs[:5]]
            st.markdown("**Select stations to book:**")
            
            selected = []
            for opt in station_options:
                if st.checkbox(opt, key=f"station_{opt}"):
                    selected.append(opt)
            
            if selected:
                st.markdown("---")
                with st.form(key="booking_form"):
                    st.markdown("##### Contact Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("Your Name*", value=company_name)
                        email = st.text_input("Email*", value=company_email)
                    with col2:
                        phone = st.text_input("Phone*")
                        launch = st.date_input("Preferred Launch Date", min_value=datetime.now().date())
                    notes = st.text_area("Campaign Details / Requirements")
                    
                    if st.form_submit_button("📞 Submit Booking Request", use_container_width=True):
                        if name and email and phone:
                            bid = create_booking(st.session_state.company_id, selected, campaign_goal, budget, duration, 
                                                target_audience, region_type, name, email, phone, notes)
                            if bid:
                                st.success(f"✅ Booking #{bid} submitted! Pending admin approval.")
                                st.balloons()
                                st.session_state.recs = None
                                st.rerun()
                        else:
                            st.error("Please fill in all contact fields")
            else:
                st.info("👆 Select at least one station above to continue")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 2: My Bookings
    with tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">📋 My Booking Requests</p>', unsafe_allow_html=True)
        
        bookings = get_bookings(st.session_state.company_id, selected_year, selected_month)
        if not bookings.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total", booking_stats['total'])
            with col2:
                st.metric("Pending", booking_stats['pending_approval'])
            with col3:
                st.metric("Approved", booking_stats['approved'])
            with col4:
                st.metric("Confirmed", booking_stats['confirmed'])
            st.markdown("---")
            
            for _, b in bookings.iterrows():
                if b['status'] == 'pending_approval':
                    badge = "badge-pending"
                    text = "PENDING APPROVAL"
                    border_class = "booking-card-pending"
                elif b['status'] == 'approved':
                    badge = "badge-approved"
                    text = "APPROVED - READY TO CONFIRM"
                    border_class = "booking-card-approved"
                elif b['status'] == 'confirmed':
                    badge = "badge-confirmed"
                    text = "CONFIRMED"
                    border_class = "booking-card-confirmed"
                else:
                    badge = "badge-pending"
                    text = b['status'].upper()
                    border_class = "booking-card-pending"
                
                st.markdown(f"""
                <div class="booking-card {border_class}">
                    <div class="booking-header">
                        <span class="booking-id">Booking #{b['booking_id']}</span>
                        <span class="booking-date">{format_date(b['request_date'])}</span>
                    </div>
                    <div class="booking-details">
                        <div class="booking-detail-item"><span class="booking-detail-label">Stations:</span> {b.get('selected_stations', b['station_name'])}</div>
                        <div class="booking-detail-item"><span class="booking-detail-label">Budget:</span> {format_currency(b['budget_kes'])}</div>
                        <div class="booking-detail-item"><span class="booking-detail-label">Duration:</span> {b['duration_days']} days</div>
                        <div class="booking-detail-item"><span class="booking-detail-label">Goal:</span> {b.get('campaign_goal', 'N/A')}</div>
                    </div>
                    <div style="margin-top: 0.5rem;">
                        <span class="{badge}">{text}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if b['status'] == 'approved':
                    if st.button(f"✅ Confirm Booking", key=f"confirm_{b['booking_id']}"):
                        update_booking_status(b['booking_id'], 'confirmed')
                        st.success("Booking confirmed!")
                        st.rerun()
                elif b['status'] == 'pending_approval':
                    st.info("⏳ Waiting for admin approval...")
                st.markdown("---")
        else:
            st.info("No bookings found for selected period. Generate recommendations and submit a booking.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 3: My Leads
    with tab3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">👥 My Leads</p>', unsafe_allow_html=True)
        
        with st.expander("📝 Demo: Submit a Test Lead", expanded=False):
            test_name = st.text_input("Name", "John Kamau")
            test_email = st.text_input("Email", "john@example.com")
            test_phone = st.text_input("Phone", "+254712345678")
            test_product = st.text_input("Product Interest", "Your Service")
            test_msg = st.text_area("Message", "I'm very interested! Please call me.")
            if st.button("Submit Test Lead"):
                add_lead(st.session_state.company_id, test_name, test_email, test_phone, test_product, test_msg, "Website")
                st.success("Test lead added!")
                st.rerun()
        
        leads = get_leads(st.session_state.company_id, selected_year, selected_month)
        if not leads.empty:
            st.markdown(f"#### Your Leads ({len(leads[leads['status'] == 'new'])} new)")
            for _, lead in leads.iterrows():
                status_badge = '<span class="badge-new">NEW</span>' if lead['status'] == 'new' else '<span class="badge-contacted">CONTACTED</span>' if lead['status'] == 'contacted' else '<span class="badge-converted">CONVERTED</span>'
                st.markdown(f"""
                <div class="lead-card">
                    <div class="lead-header">
                        <span class="lead-name">{lead['lead_name']}</span>
                        <span>{status_badge}</span>
                    </div>
                    <div class="lead-contact">
                        <span>📞 {lead['lead_phone']}</span>
                        <span>📧 {lead['lead_email']}</span>
                    </div>
                    <div class="lead-message">
                        <strong>💬 Interest:</strong> {lead['interest_product']}<br>
                        <strong>📝 Message:</strong> {lead['message'][:150] if lead['message'] else 'No message'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if lead['status'] == 'new':
                    if st.button(f"📞 Mark Contacted", key=f"contact_lead_{lead['lead_id']}"):
                        update_lead_status(lead['lead_id'], 'contacted')
                        st.rerun()
                st.markdown("---")
            
            # Lead statistics
            st.markdown("#### 📊 Lead Status Summary")
            status_counts = leads.groupby('status').size().reset_index(name='count')
            st.dataframe(status_counts, use_container_width=True, hide_index=True)
        else:
            st.info("No leads found for selected period. Use the demo form above to test lead capture.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 4: Media Directory
    with tab4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">📺 📻 Media Directory</p>', unsafe_allow_html=True)
        
        region_filter = st.selectbox("Filter by Region", ["All", "National", "Coast", "Western", "Central"])
        
        for station in get_all_stations():
            if region_filter == "All" or station['region'] == region_filter:
                with st.expander(f"📺 {station['name']} ({station['media_type']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Region:** {station['region']}")
                        st.write(f"**Reach:** {station['reach']:,}")
                    if station['contacts']:
                        with col2:
                            st.write("**Contact:**")
                            st.write(f"📞 {station['contacts']['contact_phone']}")
                            st.write(f"📧 {station['contacts']['contact_email']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 5: Performance
    with tab5:
        df = get_company_data(st.session_state.company_id, selected_year, selected_month)
        if not df.empty:
            total_spend = df['spend_kes'].sum()
            total_revenue = df['revenue_kes'].sum()
            avg_roas = total_revenue / total_spend if total_spend > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">💰 Total Spend</div><div class="metric-value">{format_currency(total_spend)}</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">💵 Total Revenue</div><div class="metric-value">{format_currency(total_revenue)}</div></div>', unsafe_allow_html=True)
            with col3:
                roas_color = "#EF4444" if avg_roas < 2 else "#10B981"
                st.markdown(f'<div class="metric-card"><div class="metric-label">📈 ROAS</div><div class="metric-value" style="color:{roas_color};">{avg_roas:.2f}x</div></div>', unsafe_allow_html=True)
            
            campaign_roas = df.groupby('campaign_name')['roas'].mean().reset_index()
            fig = px.bar(campaign_roas, x='roas', y='campaign_name', orientation='h', color='roas', color_continuous_scale='RdYlGn')
            fig.add_vline(x=2.0, line_dash="dash", line_color="#EF4444", annotation_text="Target (2x)")
            fig.update_layout(height=400, plot_bgcolor='white', showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No campaign data available for selected period")
