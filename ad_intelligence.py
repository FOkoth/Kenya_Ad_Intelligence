"""
Ad Intelligence Kenya - Complete Platform with Lead Generation
Features: Smart Recommendations + Client Booking + Audience Response
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
import random
import uuid

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
        logo_url TEXT,
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
        status TEXT DEFAULT 'planned',
        booking_reference TEXT,
        FOREIGN KEY (company_id) REFERENCES companies (company_id)
    )
    ''')
    
    # Booking requests (advertiser expresses interest)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS booking_requests (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        station_name TEXT,
        media_type TEXT,
        preferred_time TEXT,
        budget_kes REAL,
        duration_days INTEGER,
        target_audience TEXT,
        contact_name TEXT,
        contact_email TEXT,
        contact_phone TEXT,
        status TEXT DEFAULT 'pending',
        request_date TEXT,
        notes TEXT,
        FOREIGN KEY (company_id) REFERENCES companies (company_id)
    )
    ''')
    
    # Audience leads (people responding to ads)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audience_leads (
        lead_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        campaign_id INTEGER,
        station_name TEXT,
        lead_name TEXT,
        lead_email TEXT,
        lead_phone TEXT,
        interest_product TEXT,
        message TEXT,
        source TEXT,  -- 'TV', 'Radio', 'Digital'
        created_date TEXT,
        status TEXT DEFAULT 'new',
        assigned_to TEXT,
        FOREIGN KEY (company_id) REFERENCES companies (company_id)
    )
    ''')
    
    # Ad creatives (for audience to view)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ad_creatives (
        creative_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        campaign_id INTEGER,
        title TEXT,
        description TEXT,
        offer_text TEXT,
        call_to_action TEXT,
        image_url TEXT,
        start_date TEXT,
        end_date TEXT,
        is_active INTEGER DEFAULT 1
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
    
    # Recommendations history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recommendations (
        rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        campaign_goal TEXT,
        budget_kes REAL,
        duration_days INTEGER,
        target_audience TEXT,
        target_region TEXT,
        recommended_stations TEXT,
        estimated_roas REAL,
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
        
        # Sample companies
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
        margin-bottom: 0.5rem;
    }
    .rec-card h4 { color: #C6A43F; margin: 0 0 0.5rem 0; font-size: 0.9rem; }
    .rec-card p { margin: 0.25rem 0; font-size: 0.8rem; }
    
    .success-card {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        border-radius: 12px;
        padding: 1rem;
        color: white;
    }
    
    .lead-card {
        background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%);
        border-radius: 12px;
        padding: 1rem;
        color: white;
        margin-bottom: 1rem;
    }
    
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
    
    .booking-card {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .badge-new {
        background: #10B981;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.7rem;
        display: inline-block;
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
    booking_ref = str(uuid.uuid4())[:8].upper()
    cursor.execute('''
    INSERT INTO media_logs (company_id, station_name, media_type, spot_time, duration_seconds, cost_kes, estimated_reach, log_date, status, booking_reference)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (company_id, station_name, media_type, spot_time, duration, cost, reach, datetime.now().isoformat(), 'planned', booking_ref))
    conn.commit()
    conn.close()
    return booking_ref

def save_recommendation(company_id, campaign_goal, budget, duration, audience, region, stations, estimated_roas):
    """Save recommendation for future reference"""
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO recommendations (company_id, campaign_goal, budget_kes, duration_days, target_audience, target_region, recommended_stations, estimated_roas, created_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (company_id, campaign_goal, budget, duration, audience, region, stations, estimated_roas, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return True

def create_booking_request(company_id, station_name, media_type, preferred_time, budget, duration, audience, contact_name, contact_email, contact_phone, notes=""):
    """Create a booking request from advertiser"""
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO booking_requests (company_id, station_name, media_type, preferred_time, budget_kes, duration_days, target_audience, contact_name, contact_email, contact_phone, status, request_date, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (company_id, station_name, media_type, preferred_time, budget, duration, audience, contact_name, contact_email, contact_phone, 'pending', datetime.now().isoformat(), notes))
    booking_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return booking_id

def add_audience_lead(company_id, campaign_id, station_name, name, email, phone, product_interest, message, source):
    """Add a lead from audience responding to ad"""
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO audience_leads (company_id, campaign_id, station_name, lead_name, lead_email, lead_phone, interest_product, message, source, created_date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (company_id, campaign_id, station_name, name, email, phone, product_interest, message, source, datetime.now().isoformat(), 'new'))
    lead_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return lead_id

def get_booking_requests(company_id):
    """Get all booking requests for a company"""
    conn = sqlite3.connect('ad_intelligence.db')
    df = pd.read_sql_query('''
        SELECT * FROM booking_requests 
        WHERE company_id = ? 
        ORDER BY request_date DESC
    ''', conn, params=(company_id,))
    conn.close()
    return df

def get_audience_leads(company_id):
    """Get all audience leads for a company"""
    conn = sqlite3.connect('ad_intelligence.db')
    df = pd.read_sql_query('''
        SELECT * FROM audience_leads 
        WHERE company_id = ? 
        ORDER BY created_date DESC
    ''', conn, params=(company_id,))
    conn.close()
    return df

def update_lead_status(lead_id, status):
    """Update lead status (new, contacted, converted, lost)"""
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE audience_leads SET status = ? WHERE lead_id = ?", (status, lead_id))
    conn.commit()
    conn.close()
    return True

def update_booking_status(booking_id, status):
    """Update booking request status"""
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE booking_requests SET status = ? WHERE booking_id = ?", (status, booking_id))
    conn.commit()
    conn.close()
    return True

# ============================================================================
# STATION DATABASE WITH REGION FILTERING
# ============================================================================
class StationDatabase:
    """Complete station database with region filtering"""
    
    def __init__(self):
        self.stations = {
            "TV": {
                "Citizen TV": {
                    "region": "National",
                    "reach": 5000000,
                    "cost_per_spot": 250000,
                    "primary_audience": ["Mass Market", "Families", "General"],
                    "age_group": "25-55",
                    "best_for": ["Brand Awareness", "Mass Market Products", "Telecom", "Banking"],
                    "price_tier": "Premium"
                },
                "KTN": {
                    "region": "National",
                    "reach": 3000000,
                    "cost_per_spot": 200000,
                    "primary_audience": ["Professionals", "News Viewers", "Urban"],
                    "age_group": "30-50",
                    "best_for": ["News", "Corporate", "Financial Services"],
                    "price_tier": "Premium"
                },
                "NTV": {
                    "region": "National",
                    "reach": 2800000,
                    "cost_per_spot": 220000,
                    "primary_audience": ["General", "Young Adults", "Urban"],
                    "age_group": "20-45",
                    "best_for": ["Entertainment", "Retail", "Youth Products"],
                    "price_tier": "Premium"
                },
                "KBC": {
                    "region": "National",
                    "reach": 2000000,
                    "cost_per_spot": 150000,
                    "primary_audience": ["Mass Market", "Rural", "Older Adults"],
                    "age_group": "35-65",
                    "best_for": ["Government", "Public Service", "Agriculture"],
                    "price_tier": "Standard"
                }
            },
            "Radio": {
                "Citizen Radio": {"region": "National", "reach": 2500000, "cost_per_spot": 90000, "primary_audience": ["General", "Talk Radio Listeners"], "best_for": ["Talk Shows", "News"], "price_tier": "Premium"},
                "Radio Jambo": {"region": "National", "reach": 2000000, "cost_per_spot": 75000, "primary_audience": ["Youth", "Entertainment Seekers"], "best_for": ["Youth Products", "Music"], "price_tier": "Standard"},
                "Classic 105": {"region": "National", "reach": 1500000, "cost_per_spot": 80000, "primary_audience": ["Professionals", "Urban Elite"], "best_for": ["Corporate", "Luxury"], "price_tier": "Premium"},
                "Baraka FM": {"region": "Coast", "reach": 600000, "cost_per_spot": 40000, "primary_audience": ["Religious", "Coastal Residents"], "best_for": ["Religious", "Tourism"], "price_tier": "Economy"},
                "Ramogi FM": {"region": "Western", "reach": 850000, "cost_per_spot": 35000, "primary_audience": ["Luo Community"], "best_for": ["Agriculture", "Local Products"], "price_tier": "Economy"},
                "Inooro FM": {"region": "Central", "reach": 1200000, "cost_per_spot": 45000, "primary_audience": ["Kikuyu Community"], "best_for": ["Agriculture", "Real Estate"], "price_tier": "Standard"}
            }
        }
    
    def get_stations_by_region(self, region_type):
        """Get stations based on region preference: Local, National, or Both"""
        filtered = {"TV": [], "Radio": []}
        
        for media_type, stations in self.stations.items():
            for name, info in stations.items():
                if region_type == "National" and info["region"] == "National":
                    filtered[media_type].append({"name": name, **info})
                elif region_type == "Local" and info["region"] != "National":
                    filtered[media_type].append({"name": name, **info})
                elif region_type == "Both":
                    filtered[media_type].append({"name": name, **info})
        
        return filtered
    
    def get_local_stations_by_area(self, area):
        """Get stations for specific local area"""
        local_stations = []
        area_lower = area.lower()
        
        for media_type, stations in self.stations.items():
            for name, info in stations.items():
                if info["region"] != "National":
                    if (area_lower in ["coast", "mombasa"] and info["region"] == "Coast") or \
                       (area_lower in ["western", "kisumu", "luo"] and info["region"] == "Western") or \
                       (area_lower in ["central", "kikuyu"] and info["region"] == "Central"):
                        local_stations.append({"name": name, "media_type": media_type, **info})
        
        return local_stations
    
    def get_all_local_areas(self):
        """Get list of available local areas"""
        return ["Coast Region (Mombasa)", "Western Region (Kisumu)", "Central Region (Nyeri)"]

# ============================================================================
# SMART RECOMMENDATION ENGINE
# ============================================================================
class MediaRecommendationEngine:
    """Intelligent station recommendation engine"""
    
    def __init__(self):
        self.station_db = StationDatabase()
    
    def recommend_stations(self, campaign_goal, budget, duration_days, target_audience, region_type, selected_area=None):
        """Generate station recommendations based on all inputs"""
        
        # Get stations based on region preference
        available_stations = self.station_db.get_stations_by_region(region_type)
        
        recommendations = []
        
        for media_type, stations in available_stations.items():
            for station in stations:
                score = 0
                
                # Goal matching
                if campaign_goal in station.get("best_for", []):
                    score += 30
                
                # Audience matching
                if target_audience in station.get("primary_audience", []):
                    score += 30
                
                # Budget matching
                if station["price_tier"] == "Economy" and budget < 300000:
                    score += 20
                elif station["price_tier"] == "Standard" and 200000 <= budget <= 600000:
                    score += 20
                elif station["price_tier"] == "Premium" and budget > 500000:
                    score += 20
                
                if score > 20:
                    max_spots = int(budget / station["cost_per_spot"]) if station["cost_per_spot"] > 0 else 0
                    recommendations.append({
                        "station_name": station["name"],
                        "media_type": media_type,
                        "reach": station["reach"],
                        "cost_per_spot": station["cost_per_spot"],
                        "recommended_spots": min(max_spots, 7 if duration_days <= 7 else 14),
                        "best_for": station.get("best_for", []),
                        "score": score,
                        "price_tier": station["price_tier"],
                        "region": station["region"]
                    })
        
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:5]

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
    
    selected_company = st.selectbox("Select Company", ["All Companies"] + companies['company_name'].tolist())
    
    if selected_company != "All Companies":
        company_id = companies[companies['company_name'] == selected_company]['company_id'].values[0]
        df = get_company_data(company_id)
        company_name = selected_company
    else:
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
                        color='roas', color_continuous_scale='RdYlGn')
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
# CLIENT PORTAL WITH LEAD GENERATION
# ============================================================================
def show_client_portal():
    company_id = st.session_state.company_id
    
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute("SELECT company_name, industry FROM companies WHERE company_id = ?", (company_id,))
    result = cursor.fetchone()
    company_name = result[0]
    company_industry = result[1] if result[1] else "General"
    conn.close()
    
    st.markdown(f"""
    <div class="main-header">
        <h1>Welcome, {company_name}</h1>
        <p>Your personalized advertising intelligence dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = get_company_data(company_id)
    logs_df = get_company_logs(company_id)
    bookings_df = get_booking_requests(company_id)
    leads_df = get_audience_leads(company_id)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Performance", "🎯 Smart Recommendations", "📺 TV/Radio Logs", 
        "📋 Booking Requests", "👥 Audience Leads", "📈 Media Directory"
    ])
    
    # ========================================================================
    # TAB 1: Performance Dashboard
    # ========================================================================
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
    
    # ========================================================================
    # TAB 2: SMART RECOMMENDATIONS (with Call-to-Action)
    # ========================================================================
    with tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 🎯 AI-Powered Media Recommendation Engine")
        st.markdown("Get intelligent station recommendations based on your campaign parameters")
        
        engine = MediaRecommendationEngine()
        station_db = StationDatabase()
        
        # Campaign Parameters
        st.markdown("##### 📋 Campaign Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_goal = st.selectbox(
                "Campaign Goal",
                ["Brand Awareness", "Lead Generation", "Sales", "Customer Retention", "Product Launch"]
            )
            
            budget = st.number_input("Total Budget (KES)", min_value=100000, max_value=10000000, value=500000, step=50000)
            
            duration = st.select_slider("Campaign Duration (Days)", options=[7, 14, 21, 30, 45, 60], value=14)
        
        with col2:
            target_audience = st.selectbox(
                "Target Audience",
                ["Mass Market", "Youth (18-35)", "Professionals (25-45)", "Rural Population", "Urban Consumers", "Affluent Segment"]
            )
            
            region_type = st.selectbox(
                "Target Region Type",
                ["National", "Local", "Both"],
                help="National: All Kenya, Local: Specific region, Both: Mix of national and local"
            )
            
            selected_area = None
            if region_type in ["Local", "Both"]:
                selected_area = st.selectbox("Select Local Area", station_db.get_all_local_areas())
        
        if st.button("🔍 Generate Smart Recommendations", use_container_width=True):
            # Get recommendations
            recommendations = engine.recommend_stations(
                campaign_goal=campaign_goal,
                budget=budget,
                duration_days=duration,
                target_audience=target_audience,
                region_type=region_type,
                selected_area=selected_area
            )
            
            estimated_roas = 2.5  # Simplified for demo
            
            # Save recommendation
            station_names = ", ".join([r["station_name"] for r in recommendations[:3]])
            save_recommendation(company_id, campaign_goal, budget, duration, target_audience, region_type, station_names, estimated_roas)
            
            st.markdown("---")
            st.markdown("### 📊 Your Personalized Media Plan")
            
            # ROAS Prediction
            st.markdown(f"""
            <div class="success-card">
                <h4 style="margin:0 0 0.5rem 0;">📈 Estimated Campaign Performance</h4>
                <p style="font-size:1.5rem; margin:0;"><strong>Estimated ROAS: {estimated_roas}x</strong></p>
                <p style="margin:0; opacity:0.9;">Based on your {campaign_goal} campaign targeting {target_audience}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 🏆 Recommended Stations")
            
            selected_stations = []
            
            for idx, rec in enumerate(recommendations[:3]):
                with st.container():
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        price_icon = "🟢" if rec["price_tier"] == "Economy" else "🟡" if rec["price_tier"] == "Standard" else "🔴"
                        st.markdown(f"""
                        <div class="rec-card">
                            <h4>#{idx+1} {rec['station_name']} ({rec['media_type']}) {price_icon} {rec['price_tier']}</h4>
                            <p><strong>📊 Reach:</strong> {rec['reach']:,} | <strong>💰 Cost per spot:</strong> KES {rec['cost_per_spot']:,}</p>
                            <p><strong>🎯 Best For:</strong> {', '.join(rec['best_for'][:2])}</p>
                            <p><strong>📺 Recommended Spots:</strong> {rec['recommended_spots']} per day</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_b:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"📞 Book {rec['station_name']}", key=f"book_{rec['station_name']}_{idx}"):
                            st.session_state.selected_station = rec
                            st.session_state.show_booking_form = True
                            st.rerun()
                    
                    selected_stations.append(rec)
            
            # Budget breakdown
            st.markdown("---")
            st.markdown("### 💰 Recommended Budget Allocation")
            
            total_recommended_cost = sum(r["cost_per_spot"] * r["recommended_spots"] * duration for r in recommendations[:3])
            
            if total_recommended_cost > budget:
                st.warning(f"⚠️ Your budget (KES {budget:,.0f}) is lower than the recommended plan (KES {total_recommended_cost:,.0f}).")
            else:
                st.success(f"✅ Your budget of KES {budget:,.0f} is sufficient for the recommended stations")
                
                breakdown_data = []
                for rec in recommendations[:3]:
                    rec_cost = rec["cost_per_spot"] * rec["recommended_spots"] * duration
                    breakdown_data.append({
                        "Station": rec["station_name"],
                        "Spots/Day": rec["recommended_spots"],
                        "Cost/Spot": f"KES {rec['cost_per_spot']:,}",
                        "Total Cost": f"KES {rec_cost:,.0f}",
                        "Percentage": f"{(rec_cost/budget)*100:.0f}%"
                    })
                st.dataframe(pd.DataFrame(breakdown_data), use_container_width=True, hide_index=True)
            
            # Call to Action - Express Interest
            st.markdown("---")
            st.markdown("### 📞 Ready to Launch?")
            st.markdown("Express your interest and our media buying team will contact you within 24 hours.")
            
            with st.form("booking_interest_form"):
                col1, col2 = st.columns(2)
                with col1:
                    contact_name = st.text_input("Your Name", placeholder="John Doe")
                    contact_email = st.text_input("Email Address", placeholder="john@company.com")
                with col2:
                    contact_phone = st.text_input("Phone Number", placeholder="+254 XXX XXX XXX")
                    preferred_launch = st.date_input("Preferred Launch Date", min_value=datetime.now().date())
                
                additional_notes = st.text_area("Additional Notes or Requirements", placeholder="Any specific requirements for your campaign...")
                
                if st.form_submit_button("📞 Express Interest - We'll Contact You", use_container_width=True):
                    if contact_name and contact_email and contact_phone:
                        booking_id = create_booking_request(
                            company_id, 
                            recommendations[0]["station_name"] if recommendations else "Multiple Stations",
                            recommendations[0]["media_type"] if recommendations else "Mixed",
                            preferred_launch.strftime("%Y-%m-%d"),
                            budget, duration, target_audience,
                            contact_name, contact_email, contact_phone,
                            additional_notes
                        )
                        st.success(f"✅ Thank you! Your booking request (Ref: #{booking_id}) has been submitted. Our team will contact you within 24 hours.")
                        st.balloons()
                    else:
                        st.error("Please fill in all required fields (Name, Email, Phone)")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Booking form modal (shown when user clicks Book)
        if st.session_state.get('show_booking_form', False):
            with st.expander("📞 Complete Your Booking Request", expanded=True):
                selected = st.session_state.selected_station
                
                with st.form("direct_booking_form"):
                    st.markdown(f"**Station:** {selected['station_name']} ({selected['media_type']})")
                    st.markdown(f"**Cost per spot:** KES {selected['cost_per_spot']:,}")
                    st.markdown(f"**Recommended spots/day:** {selected['recommended_spots']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        contact_name = st.text_input("Your Name*")
                        contact_email = st.text_input("Email Address*")
                    with col2:
                        contact_phone = st.text_input("Phone Number*")
                        num_spots = st.number_input("Number of Spots per Day", min_value=1, max_value=20, value=selected['recommended_spots'])
                    
                    campaign_details = st.text_area("Campaign Details", placeholder="Tell us about your campaign...")
                    
                    if st.form_submit_button("Submit Booking Request"):
                        if contact_name and contact_email and contact_phone:
                            total_cost = selected['cost_per_spot'] * num_spots * duration
                            booking_id = create_booking_request(
                                company_id, selected['station_name'], selected['media_type'],
                                datetime.now().strftime("%Y-%m-%d"), total_cost, duration,
                                target_audience, contact_name, contact_email, contact_phone,
                                campaign_details
                            )
                            st.success(f"✅ Booking request submitted! Reference: #{booking_id}")
                            st.session_state.show_booking_form = False
                            st.rerun()
                        else:
                            st.error("Please fill in all required fields")
                
                if st.button("Cancel"):
                    st.session_state.show_booking_form = False
                    st.rerun()
    
    # ========================================================================
    # TAB 3: TV/Radio Logs
    # ========================================================================
    with tab3:
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
            
            st.dataframe(logs_df[['station_name', 'media_type', 'spot_time', 'cost_kes', 'status', 'booking_reference']].head(10), use_container_width=True)
            
            csv = logs_df.to_csv(index=False)
            st.download_button("📥 Export All Logs", csv, f"media_logs_{datetime.now().strftime('%Y%m%d')}.csv")
        else:
            st.info("No airtime logs yet. Use the Smart Recommendations tab to generate your first media plan.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 4: Booking Requests
    # ========================================================================
    with tab4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 📋 Your Booking Requests")
        
        if not bookings_df.empty:
            for _, booking in bookings_df.iterrows():
                status_color = "🟡" if booking['status'] == 'pending' else "🟢" if booking['status'] == 'confirmed' else "🔴"
                st.markdown(f"""
                <div class="booking-card">
                    <p><strong>{status_color} Booking #{booking['booking_id']}</strong> - {booking['request_date'][:10]}</p>
                    <p><strong>Station:</strong> {booking['station_name']} ({booking['media_type']})</p>
                    <p><strong>Budget:</strong> KES {booking['budget_kes']:,.0f} | <strong>Duration:</strong> {booking['duration_days']} days</p>
                    <p><strong>Contact:</strong> {booking['contact_name']} - {booking['contact_email']} - {booking['contact_phone']}</p>
                    <p><strong>Status:</strong> <span class="badge-new">{booking['status'].upper()}</span></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No booking requests yet. Generate a media plan and express interest.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 5: Audience Leads (People responding to ads)
    # ========================================================================
    with tab5:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 👥 Audience Leads")
        st.markdown("People who have responded to your advertisements")
        
        # Lead generation form for audience
        with st.expander("📱 Share Your Campaign Landing Page / Response Link", expanded=False):
            st.markdown("""
            **Provide a way for your audience to respond to your ads:**
            
            You can:
            1. **SMS Short Code** - e.g., "Send 'SAF' to 12345"
            2. **WhatsApp Link** - e.g., "https://wa.me/254700000000?text=I'm%20interested"
            3. **Landing Page URL** - e.g., "https://yourcampaign.com/respond"
            4. **QR Code** - Generate and display on your ads
            """)
            
            response_method = st.selectbox("Response Method", ["SMS", "WhatsApp", "Landing Page", "QR Code"])
            response_value = st.text_input("Your Response Contact/Link")
            
            if st.button("Save Response Settings"):
                st.success("Response settings saved! Share this with your audience.")
        
        st.markdown("---")
        
        # Display incoming leads
        if not leads_df.empty:
            st.markdown(f"#### New Leads ({len(leads_df[leads_df['status'] == 'new'])} unread)")
            
            for _, lead in leads_df.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        **{lead['lead_name']}** - {lead['lead_phone']} | {lead['lead_email']}
                        - **Interested in:** {lead['interest_product']}
                        - **Source:** {lead['source']} | **Date:** {lead['created_date'][:10]}
                        - **Message:** {lead['message'][:100]}...
                        """)
                    with col2:
                        if lead['status'] == 'new':
                            if st.button(f"Mark Contacted", key=f"mark_{lead['lead_id']}"):
                                update_lead_status(lead['lead_id'], 'contacted')
                                st.rerun()
                        elif lead['status'] == 'contacted':
                            st.caption("Contacted - pending conversion")
                        elif lead['status'] == 'converted':
                            st.caption("✅ Converted to customer")
            
            # Lead statistics
            st.markdown("---")
            st.markdown("#### Lead Statistics")
            
            lead_stats = leads_df.groupby('status').size().reset_index(name='count')
            st.dataframe(lead_stats, use_container_width=True, hide_index=True)
            
            # Export leads
            csv = leads_df.to_csv(index=False)
            st.download_button("📥 Export All Leads", csv, f"audience_leads_{datetime.now().strftime('%Y%m%d')}.csv")
        else:
            st.info("No audience leads yet. When people respond to your ads, they will appear here.")
            
            # Demo lead form (for testing)
            with st.expander("📝 Demo: Submit a Test Lead"):
                st.markdown("This simulates an audience member responding to your ad.")
                test_name = st.text_input("Name", "John Kamau")
                test_email = st.text_input("Email", "john@example.com")
                test_phone = st.text_input("Phone", "+254712345678")
                test_interest = st.text_input("Interested Product", "Your Product/Service")
                test_message = st.text_area("Message", "I saw your ad and I'm interested!")
                
                if st.button("Submit Test Lead"):
                    add_audience_lead(company_id, 1, "Test Campaign", test_name, test_email, test_phone, test_interest, test_message, "Website")
                    st.success("Test lead submitted! Check the Audience Leads tab.")
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 6: Media Directory
    # ========================================================================
    with tab6:
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
                        tier_icon = "🔴" if tv['price_tier'] == "Premium" else "🟡" if tv['price_tier'] == "Standard" else "🟢"
                        st.write(f"**Price Tier:** {tier_icon} {tv['price_tier']}")
            
            if "Radio" in region_media:
                st.markdown(f"#### 📻 Radio Stations in {selected_region}")
                for radio in region_media["Radio"]:
                    with st.expander(radio['name']):
                        st.write(f"**Reach:** {radio['reach']}")
                        st.write(f"**Format:** {radio['format']}")
                        tier_icon = "🔴" if radio['price_tier'] == "Premium" else "🟡" if radio['price_tier'] == "Standard" else "🟢"
                        st.write(f"**Price Tier:** {tier_icon} {radio['price_tier']}")

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
# MAIN APP ROUTING
# ============================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.show_booking_form = False
    st.session_state.selected_station = None

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
            st.session_state.show_booking_form = False
            st.session_state.selected_station = None
            st.rerun()
else:
    show_login()

# Footer
st.markdown("""
<div class="footer">
    <p>Ad Intelligence Kenya | AI-Powered Media Recommendations & Lead Generation</p>
</div>
""", unsafe_allow_html=True)
