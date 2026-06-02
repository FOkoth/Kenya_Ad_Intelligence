"""
Ad Intelligence Kenya - Complete Platform
Includes: Admin Dashboard + Client Portal + TV/Radio Logs
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
import random

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Ad Intelligence Kenya",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# DATABASE SETUP (Auto-runs on first load)
# ============================================================================
def init_database():
    """Initialize database with all tables"""
    
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'client',
        company_id INTEGER,
        created_date TEXT
    )
    ''')
    
    # Companies table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT UNIQUE NOT NULL,
        industry TEXT,
        email TEXT,
        phone TEXT,
        created_date TEXT,
        status TEXT DEFAULT 'active'
    )
    ''')
    
    # Campaigns table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS campaigns (
        campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        campaign_name TEXT,
        platform TEXT,
        spend_kes REAL,
        revenue_kes REAL,
        roas REAL,
        date TEXT,
        FOREIGN KEY (company_id) REFERENCES companies (company_id)
    )
    ''')
    
    # Media logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS media_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        campaign_id INTEGER,
        station_name TEXT,
        media_type TEXT,
        spot_time TEXT,
        duration_seconds INTEGER,
        cost_kes REAL,
        estimated_reach INTEGER,
        log_date TEXT,
        FOREIGN KEY (company_id) REFERENCES companies (company_id)
    )
    ''')
    
    # Products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        product_name TEXT,
        category TEXT,
        target_audience TEXT,
        created_date TEXT,
        FOREIGN KEY (company_id) REFERENCES companies (company_id)
    )
    ''')
    
    # Check if default users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Admin user
        cursor.execute('''
        INSERT INTO users (username, password, role, company_id, created_date)
        VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin123', 'admin', None, datetime.now().isoformat()))
        
        # Sample companies and client users
        companies = [
            ('Safaricom', 'Telecommunications', 'advertising@safaricom.com', '+254700000000'),
            ('KCB Bank', 'Financial Services', 'marketing@kcb.co.ke', '+254711000000'),
            ('Tourism Kenya', 'Tourism', 'info@tourism.go.ke', '+254730000000'),
            ('Toyota Kenya', 'Automotive', 'marketing@toyota.co.ke', '+254721000000'),
        ]
        
        for company in companies:
            cursor.execute('''
            INSERT INTO companies (company_name, industry, email, phone, created_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (company[0], company[1], company[2], company[3], datetime.now().isoformat(), 'active'))
            
            company_id = cursor.lastrowid
            username = company[0].lower().replace(' ', '')
            
            cursor.execute('''
            INSERT INTO users (username, password, role, company_id, created_date)
            VALUES (?, ?, ?, ?, ?)
            ''', (username, 'client123', 'client', company_id, datetime.now().isoformat()))
            
            # Generate sample campaign data
            for day in range(30):
                date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
                spend = random.uniform(5000, 50000)
                revenue = spend * random.uniform(0.5, 4.0)
                cursor.execute('''
                INSERT INTO campaigns (company_id, campaign_name, platform, spend_kes, revenue_kes, roas, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (company_id, f"{company[0]} Campaign", random.choice(['Meta', 'Google', 'TikTok']), 
                      spend, revenue, revenue/spend, date))
    
    conn.commit()
    conn.close()
    return True

# Run database initialization
init_database()

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #004953 0%, #006B7A 100%);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.75rem; }
    .main-header p { color: rgba(255,255,255,0.85); margin: 0.25rem 0 0 0; }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-left: 3px solid #C6A43F;
        text-align: center;
    }
    .metric-value { font-size: 1.5rem; font-weight: 700; color: #004953; }
    .metric-label { font-size: 0.7rem; color: #64748B; text-transform: uppercase; }
    
    .section-card {
        background: white;
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        border: 1px solid #E2E8F0;
    }
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1E293B;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #C6A43F;
        display: inline-block;
    }
    
    .rec-card {
        background: linear-gradient(135deg, #004953 0%, #003540 100%);
        border-radius: 12px;
        padding: 1rem;
        color: white;
    }
    .rec-card h4 { color: #C6A43F; margin: 0 0 0.5rem 0; font-size: 0.9rem; }
    .rec-card p { margin: 0.25rem 0; font-size: 0.8rem; }
    
    .footer {
        text-align: center;
        padding: 1rem;
        margin-top: 1.5rem;
        background: #F8FAFC;
        border-radius: 12px;
        font-size: 0.7rem;
        color: #64748B;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: #F1F5F9;
        padding: 0.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.25rem;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: #004953;
        color: white;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATABASE HELPER FUNCTIONS
# ============================================================================
def get_company_data(company_id):
    """Get campaign data for a specific company"""
    conn = sqlite3.connect('ad_intelligence.db')
    df = pd.read_sql_query('''
        SELECT * FROM campaigns 
        WHERE company_id = ? 
        ORDER BY date DESC
    ''', conn, params=(company_id,))
    conn.close()
    return df

def get_all_companies():
    """Get all active companies"""
    conn = sqlite3.connect('ad_intelligence.db')
    df = pd.read_sql_query("SELECT company_id, company_name, industry FROM companies WHERE status = 'active'", conn)
    conn.close()
    return df

def get_company_logs(company_id):
    """Get media logs for a specific company"""
    conn = sqlite3.connect('ad_intelligence.db')
    df = pd.read_sql_query('''
        SELECT * FROM media_logs 
        WHERE company_id = ? 
        ORDER BY log_date DESC
    ''', conn, params=(company_id,))
    conn.close()
    return df

def add_media_log(company_id, station_name, media_type, spot_time, duration, cost, reach):
    """Add a new media log entry"""
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO media_logs (company_id, station_name, media_type, spot_time, duration_seconds, cost_kes, estimated_reach, log_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (company_id, station_name, media_type, spot_time, duration, cost, reach, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return True

def get_station_cost(station_name):
    """Get cost for a station"""
    costs = {
        'Citizen TV': 250000, 'KTN': 200000, 'NTV': 220000, 'KBC': 150000,
        'Citizen Radio': 90000, 'Radio Jambo': 75000, 'Classic 105': 80000,
        'Baraka FM': 40000, 'Milele FM': 35000, 'Ramogi FM': 35000,
        'Inooro FM': 45000, 'Kameme FM': 40000
    }
    return costs.get(station_name, 50000)

def get_station_reach(station_name):
    """Get reach for a station"""
    reaches = {
        'Citizen TV': 5000000, 'KTN': 3000000, 'NTV': 2800000, 'KBC': 2000000,
        'Citizen Radio': 2500000, 'Radio Jambo': 2000000, 'Classic 105': 1500000,
        'Baraka FM': 600000, 'Milele FM': 450000, 'Ramogi FM': 850000,
        'Inooro FM': 1200000, 'Kameme FM': 1000000
    }
    return reaches.get(station_name, 500000)

# ============================================================================
# KENYAN MEDIA DIRECTORY
# ============================================================================
def get_kenyan_media():
    return {
        "Nairobi Metropolitan": {
            "TV": [
                {"name": "Citizen TV", "reach": "5,000,000", "format": "General", "price_tier": "Premium"},
                {"name": "KTN", "reach": "3,000,000", "format": "News", "price_tier": "Premium"},
                {"name": "NTV", "reach": "2,800,000", "format": "News/Entertainment", "price_tier": "Premium"},
                {"name": "KBC", "reach": "2,000,000", "format": "Public", "price_tier": "Standard"},
            ],
            "Radio": [
                {"name": "Citizen Radio", "reach": "2,500,000", "format": "News/Talk", "price_tier": "Premium"},
                {"name": "Radio Jambo", "reach": "2,000,000", "format": "Entertainment", "price_tier": "Standard"},
                {"name": "Classic 105", "reach": "1,500,000", "format": "Adult Contemporary", "price_tier": "Premium"},
            ]
        },
        "Coast Region": {
            "Radio": [
                {"name": "Baraka FM", "reach": "600,000", "format": "Religious/Talk", "price_tier": "Economy"},
                {"name": "Milele FM", "reach": "450,000", "format": "Entertainment", "price_tier": "Economy"},
            ]
        },
        "Western Region": {
            "Radio": [
                {"name": "Ramogi FM", "reach": "850,000", "format": "Vernacular", "price_tier": "Economy"},
                {"name": "Lake Victoria FM", "reach": "700,000", "format": "Vernacular", "price_tier": "Economy"},
            ]
        },
        "Central Region": {
            "Radio": [
                {"name": "Inooro FM", "reach": "1,200,000", "format": "Vernacular", "price_tier": "Standard"},
                {"name": "Kameme FM", "reach": "1,000,000", "format": "Vernacular", "price_tier": "Standard"},
            ]
        }
    }

# ============================================================================
# LOGIN SYSTEM
# ============================================================================
def check_login(username, password):
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, role, company_id FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result

def show_login():
    st.markdown("""
    <div class="main-header">
        <h1>Ad Intelligence Kenya</h1>
        <p>Data-driven advertising analytics platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            user = check_login(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.session_state.role = user[2]
                st.session_state.company_id = user[3]
                st.rerun()
            else:
                st.error("Invalid username or password")
        
        st.markdown("---")
        st.caption("Demo Accounts:")
        st.caption("Admin: username='admin', password='admin123'")
        st.caption("Client: username='safaricom', password='client123'")

# ============================================================================
# ADMIN DASHBOARD
# ============================================================================
def show_admin_dashboard():
    st.markdown("""
    <div class="main-header">
        <h1>Admin Dashboard</h1>
        <p>System-wide advertising intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    companies = get_all_companies()
    
    # Company selector
    selected_company = st.selectbox("Select Company", ["All Companies"] + companies['company_name'].tolist())
    
    if selected_company != "All Companies":
        company_id = companies[companies['company_name'] == selected_company]['company_id'].values[0]
        df = get_company_data(company_id)
        company_name = selected_company
    else:
        # Combine all company data
        all_data = []
        for _, company in companies.iterrows():
            company_df = get_company_data(company['company_id'])
            company_df['company_name'] = company['company_name']
            all_data.append(company_df)
        df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
        company_name = "All Companies"
    
    if not df.empty:
        total_spend = df['spend_kes'].sum()
        total_revenue = df['revenue_kes'].sum()
        avg_roas = total_revenue / total_spend if total_spend > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">💰 Total Spend</div><div class="metric-value">KES {total_spend:,.0f}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">💵 Total Revenue</div><div class="metric-value">KES {total_revenue:,.0f}</div></div>', unsafe_allow_html=True)
        with col3:
            roas_color = "#EF4444" if avg_roas < 2 else "#10B981"
            st.markdown(f'<div class="metric-card"><div class="metric-label">📈 Avg ROAS</div><div class="metric-value" style="color:{roas_color};">{avg_roas:.2f}x</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">🏢 Company</div><div class="metric-value">{company_name}</div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            campaign_roas = df.groupby('campaign_name')['roas'].mean().reset_index()
            campaign_roas = campaign_roas.sort_values('roas', ascending=True)
            fig = px.bar(campaign_roas, x='roas', y='campaign_name', orientation='h',
                        color='roas', color_continuous_scale='RdYlGn',
                        labels={'roas': 'ROAS (x)', 'campaign_name': ''})
            fig.add_vline(x=2.0, line_dash="dash", line_color="#EF4444")
            fig.update_layout(height=400, plot_bgcolor='white', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            daily = df.groupby('date').agg({'spend_kes': 'sum', 'revenue_kes': 'sum'}).reset_index()
            daily['date'] = pd.to_datetime(daily['date'])
            daily = daily.sort_values('date')
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily['date'], y=daily['spend_kes'], name='Spend', line=dict(color='#004953', width=2)))
            fig.add_trace(go.Scatter(x=daily['date'], y=daily['revenue_kes'], name='Revenue', line=dict(color='#C6A43F', width=2)))
            fig.update_layout(height=400, plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No campaign data available")

# ============================================================================
# CLIENT PORTAL
# ============================================================================
def show_client_portal():
    company_id = st.session_state.company_id
    
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute("SELECT company_name FROM companies WHERE company_id = ?", (company_id,))
    company_name = cursor.fetchone()[0]
    conn.close()
    
    st.markdown(f"""
    <div class="main-header">
        <h1>Welcome, {company_name}</h1>
        <p>Your personalized advertising intelligence dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = get_company_data(company_id)
    logs_df = get_company_logs(company_id)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance", "📺 TV/Radio Logs", "🎯 Campaign Intelligence", "📈 Media Directory"])
    
    # TAB 1: Performance
    with tab1:
        if not df.empty:
            total_spend = df['spend_kes'].sum()
            total_revenue = df['revenue_kes'].sum()
            avg_roas = total_revenue / total_spend if total_spend > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">💰 Total Spend</div><div class="metric-value">KES {total_spend:,.0f}</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">💵 Total Revenue</div><div class="metric-value">KES {total_revenue:,.0f}</div></div>', unsafe_allow_html=True)
            with col3:
                roas_color = "#EF4444" if avg_roas < 2 else "#10B981"
                st.markdown(f'<div class="metric-card"><div class="metric-label">📈 Your ROAS</div><div class="metric-value" style="color:{roas_color};">{avg_roas:.2f}x</div></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                campaign_roas = df.groupby('campaign_name')['roas'].mean().reset_index()
                fig = px.bar(campaign_roas, x='roas', y='campaign_name', orientation='h',
                            color='roas', color_continuous_scale='RdYlGn')
                fig.add_vline(x=2.0, line_dash="dash", line_color="#EF4444")
                fig.update_layout(height=350, plot_bgcolor='white', showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                platform_roas = df.groupby('platform')['roas'].mean().reset_index()
                fig = px.pie(platform_roas, values='roas', names='platform', hole=0.4,
                            color_discrete_sequence=['#004953', '#006B7A', '#C6A43F'])
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No campaign data available")
    
    # TAB 2: TV/Radio Logs
    with tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 📺 📻 Airtime Logs")
        
        if not logs_df.empty:
            total_spots = len(logs_df)
            total_cost = logs_df['cost_kes'].sum()
            total_reach = logs_df['estimated_reach'].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Spots Aired", total_spots)
            with col2:
                st.metric("Total Cost", f"KES {total_cost:,.0f}")
            with col3:
                st.metric("Total Reach", f"{total_reach:,.0f}")
            
            station_summary = logs_df.groupby('station_name').agg({
                'cost_kes': 'sum', 'estimated_reach': 'sum', 'duration_seconds': 'count'
            }).reset_index()
            station_summary.columns = ['Station', 'Total Cost', 'Total Reach', 'Spots']
            st.dataframe(station_summary, use_container_width=True)
            
            csv = logs_df.to_csv(index=False)
            st.download_button("📥 Export Logs", csv, f"media_logs.csv")
        else:
            st.info("No airtime logs yet")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.expander("➕ Add Airtime Log Manually"):
            col1, col2 = st.columns(2)
            with col1:
                station = st.selectbox("Station", [s['name'] for s in get_kenyan_media()["Nairobi Metropolitan"]["TV"] + get_kenyan_media()["Nairobi Metropolitan"]["Radio"]])
                media_type = "TV" if station in [s['name'] for s in get_kenyan_media()["Nairobi Metropolitan"]["TV"]] else "Radio"
                spot_time = st.text_input("Time (YYYY-MM-DD HH:MM:SS)", datetime.now().strftime("%Y-%m-%d 19:30:00"))
            with col2:
                duration = st.number_input("Duration (sec)", 15, 60, 30)
                cost = st.number_input("Cost (KES)", 10000, 500000, get_station_cost(station))
                reach = st.number_input("Est. Reach", 10000, 5000000, get_station_reach(station))
            
            if st.button("Add Log"):
                add_media_log(company_id, station, media_type, spot_time, duration, cost, reach)
                st.success("Log added!")
                st.rerun()
    
    # TAB 3: Campaign Intelligence
    with tab3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 🎯 Media Planner")
        
        col1, col2 = st.columns(2)
        with col1:
            campaign_goal = st.selectbox("Campaign Goal", ["Brand Awareness", "Lead Generation", "Sales", "Customer Retention"])
            budget = st.number_input("Budget (KES)", 100000, 5000000, 500000, 50000)
        with col2:
            target_region = st.selectbox("Target Region", ["Nairobi Metropolitan", "Coast Region", "Western Region", "Central Region"])
        
        if st.button("Generate Media Plan", use_container_width=True):
            if company_name == "Safaricom":
                primary_tv = "Citizen TV"
                primary_radio = "Radio Jambo"
            else:
                primary_tv = "NTV"
                primary_radio = "Citizen Radio"
            
            st.markdown("---")
            st.markdown("#### 📋 Your Media Plan")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**📺 Primary TV:** {primary_tv}")
                st.markdown(f"**📻 Primary Radio:** {primary_radio}")
                st.markdown(f"**💰 Budget:** KES {budget:,.0f}")
            with col2:
                tv_budget = budget * 0.6
                radio_budget = budget * 0.4
                st.markdown(f"**TV Allocation:** KES {tv_budget:,.0f} (60%)")
                st.markdown(f"**Radio Allocation:** KES {radio_budget:,.0f} (40%)")
            
            if st.button("Generate Logs from Plan"):
                schedule = [
                    {'station': primary_tv, 'type': 'TV', 'time': f"{datetime.now().strftime('%Y-%m-%d')} 19:30:00", 'cost': tv_budget/2, 'reach': 3000000},
                    {'station': primary_tv, 'type': 'TV', 'time': f"{datetime.now().strftime('%Y-%m-%d')} 20:00:00", 'cost': tv_budget/2, 'reach': 3000000},
                    {'station': primary_radio, 'type': 'Radio', 'time': f"{datetime.now().strftime('%Y-%m-%d')} 08:00:00", 'cost': radio_budget/2, 'reach': 1000000},
                    {'station': primary_radio, 'type': 'Radio', 'time': f"{datetime.now().strftime('%Y-%m-%d')} 17:30:00", 'cost': radio_budget/2, 'reach': 1000000},
                ]
                for spot in schedule:
                    add_media_log(company_id, spot['station'], spot['type'], spot['time'], 30, spot['cost'], spot['reach'])
                st.success("Media logs generated! Check the TV/Radio Logs tab.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 4: Media Directory
    with tab4:
        media = get_kenyan_media()
        selected_region = st.selectbox("Select Region", list(media.keys()))
        
        if selected_region:
            region_media = media[selected_region]
            if "TV" in region_media:
                st.markdown(f"#### 📺 TV Stations in {selected_region}")
                for tv in region_media["TV"]:
                    with st.expander(tv['name']):
                        st.write(f"**Reach:** {tv['reach']}")
                        st.write(f"**Format:** {tv['format']}")
                        st.write(f"**Price:** {tv['price_tier']}")
            if "Radio" in region_media:
                st.markdown(f"#### 📻 Radio Stations in {selected_region}")
                for radio in region_media["Radio"]:
                    with st.expander(radio['name']):
                        st.write(f"**Reach:** {radio['reach']}")
                        st.write(f"**Format:** {radio['format']}")
                        st.write(f"**Price:** {radio['price_tier']}")

# ============================================================================
# MAIN APP ROUTING
# ============================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    if st.session_state.role == 'admin':
        show_admin_dashboard()
    else:
        show_client_portal()
    
    # Logout button in sidebar
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
else:
    show_login()

# Footer
st.markdown("""
<div class="footer">
    <p>Ad Intelligence Kenya | Data-driven advertising analytics</p>
</div>
""", unsafe_allow_html=True)
