"""
Ad Intelligence Kenya - Complete Platform with Lead Generation
Features: Smart Recommendations + Client Booking + Audience Response + Admin Overview
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
# DATABASE SETUP WITH MIGRATION
# ============================================================================
def migrate_database():
    """Add missing columns to existing tables"""
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    
    # Check and add missing columns to media_logs
    cursor.execute("PRAGMA table_info(media_logs)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'status' not in columns:
        cursor.execute("ALTER TABLE media_logs ADD COLUMN status TEXT DEFAULT 'planned'")
    
    if 'booking_reference' not in columns:
        cursor.execute("ALTER TABLE media_logs ADD COLUMN booking_reference TEXT")
    
    # Check and add missing columns to booking_requests
    cursor.execute("PRAGMA table_info(booking_requests)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'notes' not in columns:
        cursor.execute("ALTER TABLE booking_requests ADD COLUMN notes TEXT")
    
    if 'selected_stations' not in columns:
        cursor.execute("ALTER TABLE booking_requests ADD COLUMN selected_stations TEXT")
    
    # Check and add missing columns to audience_leads
    cursor.execute("PRAGMA table_info(audience_leads)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'assigned_to' not in columns:
        cursor.execute("ALTER TABLE audience_leads ADD COLUMN assigned_to TEXT")
    
    if 'converted_date' not in columns:
        cursor.execute("ALTER TABLE audience_leads ADD COLUMN converted_date TEXT")
    
    conn.commit()
    conn.close()

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
    
    # Booking requests
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS booking_requests (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        station_name TEXT,
        selected_stations TEXT,
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
    
    # Audience leads
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
        source TEXT,
        created_date TEXT,
        status TEXT DEFAULT 'new',
        assigned_to TEXT,
        converted_date TEXT,
        FOREIGN KEY (company_id) REFERENCES companies (company_id)
    )
    ''')
    
    # Ad creatives
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
    
    # Recommendations history
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
            
            # Generate sample leads for each company
            sample_leads = [
                ("John Kamau", "john@example.com", "+254712345678", "Data Bundles", "Interested in your latest offer"),
                ("Mary Wanjiku", "mary@example.com", "+254723456789", "M-Pesa Services", "Need more information"),
                ("Peter Omondi", "peter@example.com", "+254734567890", "Home Internet", "What are your rates?"),
            ]
            for lead in sample_leads:
                cursor.execute('''
                INSERT INTO audience_leads (company_id, lead_name, lead_email, lead_phone, interest_product, message, source, created_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (company_id, lead[0], lead[1], lead[2], lead[3], lead[4], "Website", datetime.now().isoformat(), random.choice(['new', 'contacted'])))
    
    conn.commit()
    conn.close()
    return True

# Run database initialization and migration
init_database()
migrate_database()

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
    
    .booking-card {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .lead-card {
        background: #F0FDF4;
        border: 1px solid #86EFAC;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .badge-new {
        background: #10B981;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.7rem;
        display: inline-block;
    }
    
    .badge-contacted {
        background: #F59E0B;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.7rem;
        display: inline-block;
    }
    
    .badge-converted {
        background: #8B5CF6;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.7rem;
        display: inline-block;
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
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATABASE HELPER FUNCTIONS
# ============================================================================
def get_company_data(company_id):
    """Get campaign data for a specific company"""
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        df = pd.read_sql_query('''
            SELECT * FROM campaigns 
            WHERE company_id = ? 
            ORDER BY date DESC
        ''', conn, params=(company_id,))
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

def get_all_companies():
    """Get all active companies"""
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        df = pd.read_sql_query("SELECT company_id, company_name, industry, email, phone FROM companies WHERE status = 'active'", conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

def get_company_logs(company_id):
    """Get media logs for a specific company"""
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        df = pd.read_sql_query('''
            SELECT * FROM media_logs 
            WHERE company_id = ? 
            ORDER BY log_date DESC
        ''', conn, params=(company_id,))
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

def add_media_log(company_id, station_name, media_type, spot_time, duration, cost, reach):
    """Add a new media log entry"""
    try:
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
    except Exception as e:
        return None

def save_recommendation(company_id, campaign_goal, budget, duration, audience, region, stations, estimated_roas):
    """Save recommendation for future reference"""
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO recommendations (company_id, campaign_goal, budget_kes, duration_days, target_audience, target_region, recommended_stations, estimated_roas, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (company_id, campaign_goal, budget, duration, audience, region, stations, estimated_roas, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

def create_booking_request(company_id, selected_stations_list, media_type, preferred_time, budget, duration, audience, contact_name, contact_email, contact_phone, notes=""):
    """Create a booking request from advertiser with multiple stations"""
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        cursor = conn.cursor()
        selected_stations_str = ", ".join(selected_stations_list)
        primary_station = selected_stations_list[0] if selected_stations_list else "Multiple"
        
        cursor.execute('''
        INSERT INTO booking_requests (company_id, station_name, selected_stations, media_type, preferred_time, budget_kes, duration_days, target_audience, contact_name, contact_email, contact_phone, status, request_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (company_id, primary_station, selected_stations_str, media_type, preferred_time, budget, duration, audience, contact_name, contact_email, contact_phone, 'pending', datetime.now().isoformat(), notes))
        booking_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return booking_id
    except Exception as e:
        return None

def add_audience_lead(company_id, campaign_id, station_name, name, email, phone, product_interest, message, source):
    """Add a lead from audience responding to ad"""
    try:
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
    except Exception as e:
        return None

def get_booking_requests(company_id=None):
    """Get all booking requests, optionally filtered by company"""
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        if company_id:
            df = pd.read_sql_query('''
                SELECT br.*, c.company_name 
                FROM booking_requests br
                JOIN companies c ON br.company_id = c.company_id
                WHERE br.company_id = ? 
                ORDER BY br.request_date DESC
            ''', conn, params=(company_id,))
        else:
            df = pd.read_sql_query('''
                SELECT br.*, c.company_name 
                FROM booking_requests br
                JOIN companies c ON br.company_id = c.company_id
                ORDER BY br.request_date DESC
            ''', conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

def get_audience_leads(company_id=None):
    """Get all audience leads, optionally filtered by company"""
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        if company_id:
            df = pd.read_sql_query('''
                SELECT al.*, c.company_name 
                FROM audience_leads al
                JOIN companies c ON al.company_id = c.company_id
                WHERE al.company_id = ? 
                ORDER BY al.created_date DESC
            ''', conn, params=(company_id,))
        else:
            df = pd.read_sql_query('''
                SELECT al.*, c.company_name 
                FROM audience_leads al
                JOIN companies c ON al.company_id = c.company_id
                ORDER BY al.created_date DESC
            ''', conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

def update_lead_status(lead_id, status):
    """Update lead status"""
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        cursor = conn.cursor()
        converted_date = datetime.now().isoformat() if status == 'converted' else None
        cursor.execute("UPDATE audience_leads SET status = ?, converted_date = ? WHERE lead_id = ?", (status, converted_date, lead_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

def update_booking_status(booking_id, status):
    """Update booking request status"""
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE booking_requests SET status = ? WHERE booking_id = ?", (status, booking_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

def get_lead_statistics(company_id=None):
    """Get lead statistics for dashboard"""
    leads_df = get_audience_leads(company_id)
    if leads_df.empty:
        return {'total': 0, 'new': 0, 'contacted': 0, 'converted': 0, 'conversion_rate': 0}
    
    total = len(leads_df)
    new = len(leads_df[leads_df['status'] == 'new'])
    contacted = len(leads_df[leads_df['status'] == 'contacted'])
    converted = len(leads_df[leads_df['status'] == 'converted'])
    conversion_rate = (converted / total * 100) if total > 0 else 0
    
    return {
        'total': total,
        'new': new,
        'contacted': contacted,
        'converted': converted,
        'conversion_rate': round(conversion_rate, 1)
    }

def get_booking_statistics(company_id=None):
    """Get booking statistics for dashboard"""
    bookings_df = get_booking_requests(company_id)
    if bookings_df.empty:
        return {'total': 0, 'pending': 0, 'confirmed': 0, 'completed': 0}
    
    total = len(bookings_df)
    pending = len(bookings_df[bookings_df['status'] == 'pending'])
    confirmed = len(bookings_df[bookings_df['status'] == 'confirmed'])
    completed = len(bookings_df[bookings_df['status'] == 'completed'])
    
    return {
        'total': total,
        'pending': pending,
        'confirmed': confirmed,
        'completed': completed
    }

# ============================================================================
# STATION DATABASE
# ============================================================================
class StationDatabase:
    def __init__(self):
        self.stations = {
            "TV": {
                "Citizen TV": {"region": "National", "reach": 5000000, "cost_per_spot": 250000, "primary_audience": ["Mass Market"], "best_for": ["Brand Awareness", "Telecom"], "price_tier": "Premium"},
                "KTN": {"region": "National", "reach": 3000000, "cost_per_spot": 200000, "primary_audience": ["Professionals"], "best_for": ["News", "Financial"], "price_tier": "Premium"},
                "NTV": {"region": "National", "reach": 2800000, "cost_per_spot": 220000, "primary_audience": ["General"], "best_for": ["Entertainment", "Retail"], "price_tier": "Premium"},
                "KBC": {"region": "National", "reach": 2000000, "cost_per_spot": 150000, "primary_audience": ["Mass Market"], "best_for": ["Public Service"], "price_tier": "Standard"}
            },
            "Radio": {
                "Citizen Radio": {"region": "National", "reach": 2500000, "cost_per_spot": 90000, "primary_audience": ["General"], "best_for": ["Talk Shows"], "price_tier": "Premium"},
                "Radio Jambo": {"region": "National", "reach": 2000000, "cost_per_spot": 75000, "primary_audience": ["Youth"], "best_for": ["Youth Products"], "price_tier": "Standard"},
                "Classic 105": {"region": "National", "reach": 1500000, "cost_per_spot": 80000, "primary_audience": ["Professionals"], "best_for": ["Corporate"], "price_tier": "Premium"},
                "Baraka FM": {"region": "Coast", "reach": 600000, "cost_per_spot": 40000, "primary_audience": ["Religious"], "best_for": ["Tourism"], "price_tier": "Economy"},
                "Ramogi FM": {"region": "Western", "reach": 850000, "cost_per_spot": 35000, "primary_audience": ["Luo Community"], "best_for": ["Agriculture"], "price_tier": "Economy"},
                "Inooro FM": {"region": "Central", "reach": 1200000, "cost_per_spot": 45000, "primary_audience": ["Kikuyu Community"], "best_for": ["Agriculture"], "price_tier": "Standard"}
            }
        }
    
    def get_all_stations_list(self):
        """Get list of all stations for multi-select"""
        stations = []
        for media_type, station_list in self.stations.items():
            for name, info in station_list.items():
                stations.append(f"{name} ({media_type}) - {info['price_tier']}")
        return stations
    
    def get_stations_by_region(self, region_type):
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
    
    def get_all_local_areas(self):
        return ["Coast Region (Mombasa)", "Western Region (Kisumu)", "Central Region (Nyeri)"]

# ============================================================================
# SMART RECOMMENDATION ENGINE
# ============================================================================
class MediaRecommendationEngine:
    def __init__(self):
        self.station_db = StationDatabase()
    
    def recommend_stations(self, campaign_goal, budget, duration_days, target_audience, region_type, selected_area=None):
        available_stations = self.station_db.get_stations_by_region(region_type)
        recommendations = []
        
        for media_type, stations in available_stations.items():
            for station in stations:
                score = 0
                if campaign_goal in station.get("best_for", []):
                    score += 30
                if target_audience in station.get("primary_audience", []):
                    score += 30
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
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, role, company_id FROM users WHERE username = ? AND password = ?", (username, password))
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        return None

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
# ADMIN DASHBOARD WITH BOOKINGS AND LEADS
# ============================================================================
def show_admin_dashboard():
    st.markdown("""
    <div class="main-header">
        <h1>Admin Dashboard</h1>
        <p>System-wide advertising intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get all data for admin overview
    all_companies = get_all_companies()
    all_bookings = get_booking_requests()
    all_leads = get_audience_leads()
    
    # Statistics Row
    st.markdown("### 📊 Platform Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🏢 Total Companies</div>
            <div class="metric-value">{len(all_companies)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_bookings = len(all_bookings) if not all_bookings.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📋 Total Booking Requests</div>
            <div class="metric-value">{total_bookings}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_leads = len(all_leads) if not all_leads.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">👥 Total Audience Leads</div>
            <div class="metric-value">{total_leads}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        pending_bookings = len(all_bookings[all_bookings['status'] == 'pending']) if not all_bookings.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏳ Pending Bookings</div>
            <div class="metric-value">{pending_bookings}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for Admin
    admin_tab1, admin_tab2, admin_tab3, admin_tab4, admin_tab5 = st.tabs([
        "📊 Performance", "📋 All Booking Requests", "👥 All Audience Leads", "🏢 Companies", "📺 Media Directory"
    ])
    
    # ========================================================================
    # ADMIN TAB 1: Performance (Company view)
    # ========================================================================
    with admin_tab1:
        if not all_companies.empty:
            selected_company = st.selectbox("Select Company", ["All Companies"] + all_companies['company_name'].tolist())
            
            if selected_company != "All Companies":
                company_id = all_companies[all_companies['company_name'] == selected_company]['company_id'].values[0]
                df = get_company_data(company_id)
                company_name = selected_company
                
                # Company-specific lead stats
                lead_stats = get_lead_statistics(company_id)
                booking_stats = get_booking_statistics(company_id)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">👥 Leads</div><div class="metric-value">{lead_stats["total"]}</div></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">🆕 New Leads</div><div class="metric-value">{lead_stats["new"]}</div></div>', unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">✅ Converted</div><div class="metric-value">{lead_stats["converted"]}</div></div>', unsafe_allow_html=True)
                with col4:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">📋 Bookings</div><div class="metric-value">{booking_stats["total"]}</div></div>', unsafe_allow_html=True)
            else:
                df = pd.DataFrame()
                company_name = "All Companies"
            
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
                    st.markdown(f'<div class="metric-card"><div class="metric-label">📈 Avg ROAS</div><div class="metric-value" style="color:{roas_color};">{avg_roas:.2f}x</div></div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if 'campaign_name' in df.columns and 'roas' in df.columns:
                        campaign_roas = df.groupby('campaign_name')['roas'].mean().reset_index()
                        campaign_roas = campaign_roas.sort_values('roas', ascending=True)
                        fig = px.bar(campaign_roas, x='roas', y='campaign_name', orientation='h',
                                    color='roas', color_continuous_scale='RdYlGn')
                        fig.add_vline(x=2.0, line_dash="dash", line_color="#EF4444")
                        fig.update_layout(height=400, plot_bgcolor='white', showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No campaign data available")
    
    # ========================================================================
    # ADMIN TAB 2: All Booking Requests
    # ========================================================================
    with admin_tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 📋 All Booking Requests")
        
        if not all_bookings.empty:
            for _, booking in all_bookings.iterrows():
                status_color = "🟡" if booking['status'] == 'pending' else "🟢" if booking['status'] == 'confirmed' else "🔴"
                
                # Display stations selected
                stations_display = booking.get('selected_stations', booking['station_name'])
                
                st.markdown(f"""
                <div class="booking-card">
                    <p><strong>{status_color} Booking #{booking['booking_id']}</strong> - {booking['request_date'][:10] if booking['request_date'] else 'N/A'}</p>
                    <p><strong>Company:</strong> {booking['company_name']}</p>
                    <p><strong>Stations Requested:</strong> {stations_display}</p>
                    <p><strong>Budget:</strong> KES {booking['budget_kes']:,.0f} | <strong>Duration:</strong> {booking['duration_days']} days</p>
                    <p><strong>Contact:</strong> {booking['contact_name']} - {booking['contact_email']} - {booking['contact_phone']}</p>
                    <p><strong>Target Audience:</strong> {booking['target_audience']}</p>
                    <p><strong>Preferred Launch:</strong> {booking['preferred_time']}</p>
                    <p><strong>Status:</strong> <span class="badge-new">{booking['status'].upper()}</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Status update buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if booking['status'] == 'pending':
                        if st.button(f"✅ Confirm", key=f"confirm_{booking['booking_id']}"):
                            update_booking_status(booking['booking_id'], 'confirmed')
                            st.rerun()
                with col2:
                    if booking['status'] in ['pending', 'confirmed']:
                        if st.button(f"📞 Mark Completed", key=f"complete_{booking['booking_id']}"):
                            update_booking_status(booking['booking_id'], 'completed')
                            st.rerun()
                with col3:
                    if booking['status'] == 'pending':
                        if st.button(f"❌ Reject", key=f"reject_{booking['booking_id']}"):
                            update_booking_status(booking['booking_id'], 'rejected')
                            st.rerun()
                
                st.markdown("---")
        else:
            st.info("No booking requests yet")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # ADMIN TAB 3: All Audience Leads
    # ========================================================================
    with admin_tab3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 👥 All Audience Leads")
        
        if not all_leads.empty:
            # Filter by status
            status_filter = st.selectbox("Filter by Status", ["All", "New", "Contacted", "Converted"])
            
            filtered_leads = all_leads
            if status_filter != "All":
                filtered_leads = all_leads[all_leads['status'] == status_filter.lower()]
            
            for _, lead in filtered_leads.iterrows():
                if lead['status'] == 'new':
                    badge = '<span class="badge-new">NEW</span>'
                elif lead['status'] == 'contacted':
                    badge = '<span class="badge-contacted">CONTACTED</span>'
                else:
                    badge = '<span class="badge-converted">CONVERTED</span>'
                
                st.markdown(f"""
                <div class="lead-card">
                    <p><strong>{lead['lead_name']}</strong> {badge} - {lead['created_date'][:10] if lead['created_date'] else 'N/A'}</p>
                    <p><strong>Company:</strong> {lead['company_name']} | <strong>Phone:</strong> {lead['lead_phone']} | <strong>Email:</strong> {lead['lead_email']}</p>
                    <p><strong>Interested in:</strong> {lead['interest_product']}</p>
                    <p><strong>Message:</strong> {lead['message'][:200] if lead['message'] else 'No message'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Status update buttons
                if lead['status'] == 'new':
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"📞 Mark Contacted", key=f"contact_{lead['lead_id']}"):
                            update_lead_status(lead['lead_id'], 'contacted')
                            st.rerun()
                    with col2:
                        if st.button(f"✅ Mark Converted", key=f"convert_{lead['lead_id']}"):
                            update_lead_status(lead['lead_id'], 'converted')
                            st.rerun()
                elif lead['status'] == 'contacted':
                    if st.button(f"✅ Mark Converted", key=f"convert_{lead['lead_id']}"):
                        update_lead_status(lead['lead_id'], 'converted')
                        st.rerun()
                
                st.markdown("---")
            
            # Statistics
            st.markdown("#### 📊 Lead Statistics by Company")
            lead_stats_by_company = all_leads.groupby(['company_name', 'status']).size().unstack(fill_value=0).reset_index()
            st.dataframe(lead_stats_by_company, use_container_width=True)
            
            # Export
            csv = all_leads.to_csv(index=False)
            st.download_button("📥 Export All Leads", csv, f"all_leads_{datetime.now().strftime('%Y%m%d')}.csv")
        else:
            st.info("No audience leads yet")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # ADMIN TAB 4: Companies
    # ========================================================================
    with admin_tab4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 🏢 Registered Companies")
        
        if not all_companies.empty:
            st.dataframe(all_companies, use_container_width=True, hide_index=True)
        else:
            st.info("No companies registered")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # ADMIN TAB 5: Media Directory
    # ========================================================================
    with admin_tab5:
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
                        st.write(f"**Price Tier:** {tv['price_tier']}")
            
            if "Radio" in region_media:
                st.markdown(f"#### 📻 Radio Stations in {selected_region}")
                for radio in region_media["Radio"]:
                    with st.expander(radio['name']):
                        st.write(f"**Reach:** {radio['reach']}")
                        st.write(f"**Format:** {radio['format']}")
                        st.write(f"**Price Tier:** {radio['price_tier']}")

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
# CLIENT PORTAL
# ============================================================================
def show_client_portal():
    company_id = st.session_state.company_id
    
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        cursor = conn.cursor()
        cursor.execute("SELECT company_name, industry FROM companies WHERE company_id = ?", (company_id,))
        result = cursor.fetchone()
        company_name = result[0] if result else "Your Company"
        company_industry = result[1] if result and result[1] else "General"
        conn.close()
    except Exception as e:
        company_name = "Your Company"
        company_industry = "General"
    
    st.markdown(f"""
    <div class="main-header">
        <h1>Welcome, {company_name}</h1>
        <p>Your personalized advertising intelligence dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get lead statistics for dashboard
    lead_stats = get_lead_statistics(company_id)
    booking_stats = get_booking_statistics(company_id)
    
    # Lead Metrics Row on Dashboard
    st.markdown("### 📊 Your Lead Performance")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">👥 Total Leads</div>
            <div class="metric-value">{lead_stats['total']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🆕 New Leads</div>
            <div class="metric-value">{lead_stats['new']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📞 Contacted</div>
            <div class="metric-value">{lead_stats['contacted']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">✅ Converted</div>
            <div class="metric-value">{lead_stats['converted']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📈 Conversion Rate</div>
            <div class="metric-value">{lead_stats['conversion_rate']}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    df = get_company_data(company_id)
    logs_df = get_company_logs(company_id)
    bookings_df = get_booking_requests(company_id)
    leads_df = get_audience_leads(company_id)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Performance", "🎯 Smart Recommendations", "📺 TV/Radio Logs", "📋 Booking Requests", "👥 Audience Leads"
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
                if 'campaign_name' in df.columns and 'roas' in df.columns:
                    campaign_roas = df.groupby('campaign_name')['roas'].mean().reset_index()
                    fig = px.bar(campaign_roas, x='roas', y='campaign_name', orientation='h',
                                color='roas', color_continuous_scale='RdYlGn')
                    fig.add_vline(x=2.0, line_dash="dash", line_color="#EF4444")
                    fig.update_layout(height=350, plot_bgcolor='white', showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            with col2:
                if 'platform' in df.columns and 'roas' in df.columns:
                    platform_roas = df.groupby('platform')['roas'].mean().reset_index()
                    fig = px.pie(platform_roas, values='roas', names='platform', hole=0.4,
                                color_discrete_sequence=['#004953', '#006B7A', '#C6A43F'])
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No campaign data available")
    
    # ========================================================================
    # TAB 2: Smart Recommendations with Multi-Station Selection
    # ========================================================================
    with tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 🎯 AI-Powered Media Recommendation Engine")
        
        engine = MediaRecommendationEngine()
        station_db = StationDatabase()
        
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
            region_type = st.selectbox("Target Region Type", ["National", "Local", "Both"])
            selected_area = None
            if region_type in ["Local", "Both"]:
                selected_area = st.selectbox("Select Local Area", station_db.get_all_local_areas())
        
        if st.button("🔍 Generate Smart Recommendations", use_container_width=True):
            recommendations = engine.recommend_stations(
                campaign_goal=campaign_goal,
                budget=budget,
                duration_days=duration,
                target_audience=target_audience,
                region_type=region_type,
                selected_area=selected_area
            )
            
            estimated_roas = 2.5
            station_names = ", ".join([r["station_name"] for r in recommendations[:3]])
            save_recommendation(company_id, campaign_goal, budget, duration, target_audience, region_type, station_names, estimated_roas)
            
            st.markdown("---")
            st.markdown(f"""
            <div class="success-card">
                <h4 style="margin:0 0 0.5rem 0;">📈 Estimated Campaign Performance</h4>
                <p style="font-size:1.5rem; margin:0;"><strong>Estimated ROAS: {estimated_roas}x</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🏆 Recommended Stations")
            
            # Store recommendations in session for multi-select
            st.session_state.recommended_stations = recommendations
            
            for idx, rec in enumerate(recommendations[:5]):
                price_icon = "🟢" if rec["price_tier"] == "Economy" else "🟡" if rec["price_tier"] == "Standard" else "🔴"
                st.markdown(f"""
                <div class="rec-card">
                    <h4>#{idx+1} {rec['station_name']} ({rec['media_type']}) {price_icon} {rec['price_tier']}</h4>
                    <p><strong>📊 Reach:</strong> {rec['reach']:,} | <strong>💰 Cost per spot:</strong> KES {rec['cost_per_spot']:,}</p>
                    <p><strong>📺 Recommended Spots:</strong> {rec['recommended_spots']} per day</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Multi-station booking form
            st.markdown("---")
            st.markdown("### 📞 Book Multiple Stations")
            st.markdown("Select the stations you want to book for your campaign")
            
            # Create checkboxes for each recommended station
            station_options = [f"{r['station_name']} ({r['media_type']}) - KES {r['cost_per_spot']:,}/spot" for r in recommendations[:5]]
            selected_stations_display = st.multiselect("Select Stations to Book", station_options)
            
            # Extract selected station names
            selected_station_names = [s.split(" (")[0] for s in selected_stations_display]
            
            with st.form("multi_station_booking_form"):
                st.markdown("#### Contact Information")
                col1, col2 = st.columns(2)
                with col1:
                    contact_name = st.text_input("Your Name*", key="multi_name")
                    contact_email = st.text_input("Email Address*", key="multi_email")
                with col2:
                    contact_phone = st.text_input("Phone Number*", key="multi_phone")
                    preferred_launch = st.date_input("Preferred Launch Date", min_value=datetime.now().date())
                
                additional_notes = st.text_area("Campaign Details / Special Requirements")
                
                if st.form_submit_button("📞 Submit Booking Request for Selected Stations", use_container_width=True):
                    if contact_name and contact_email and contact_phone and selected_station_names:
                        booking_id = create_booking_request(
                            company_id, selected_station_names, "Mixed",
                            preferred_launch.strftime("%Y-%m-%d"),
                            budget, duration, target_audience,
                            contact_name, contact_email, contact_phone,
                            additional_notes
                        )
                        if booking_id:
                            st.success(f"✅ Booking request submitted! Reference: #{booking_id} for {len(selected_station_names)} station(s)")
                            st.balloons()
                        else:
                            st.error("Error submitting request")
                    elif not selected_station_names:
                        st.warning("Please select at least one station to book")
                    else:
                        st.error("Please fill in all contact fields")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 3: TV/Radio Logs
    # ========================================================================
    with tab3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 📺 📻 Airtime Logs")
        
        if not logs_df.empty:
            total_spots = len(logs_df)
            total_cost = logs_df['cost_kes'].sum() if 'cost_kes' in logs_df.columns else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Spots", total_spots)
            with col2:
                st.metric("Total Cost", f"KES {total_cost:,.0f}")
            
            display_cols = [c for c in ['station_name', 'media_type', 'spot_time', 'cost_kes'] if c in logs_df.columns]
            if display_cols:
                st.dataframe(logs_df[display_cols].head(10), use_container_width=True)
            
            csv = logs_df.to_csv(index=False)
            st.download_button("📥 Export Logs", csv, f"media_logs_{datetime.now().strftime('%Y%m%d')}.csv")
        else:
            st.info("No airtime logs yet. Generate a media plan in the Smart Recommendations tab.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 4: Booking Requests
    # ========================================================================
    with tab4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 📋 Your Booking Requests")
        
        if not bookings_df.empty:
            for _, booking in bookings_df.iterrows():
                status_icon = "🟡" if booking['status'] == 'pending' else "🟢" if booking['status'] == 'confirmed' else "🔴"
                stations_display = booking.get('selected_stations', booking['station_name'])
                
                st.markdown(f"""
                <div class="booking-card">
                    <p><strong>{status_icon} Booking #{booking['booking_id']}</strong> - {booking['request_date'][:10] if booking['request_date'] else 'N/A'}</p>
                    <p><strong>Stations:</strong> {stations_display}</p>
                    <p><strong>Budget:</strong> KES {booking['budget_kes']:,.0f} | <strong>Duration:</strong> {booking['duration_days']} days</p>
                    <p><strong>Status:</strong> <span class="badge-new">{booking['status'].upper()}</span></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No booking requests yet. Generate a media plan and submit a booking.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 5: Audience Leads
    # ========================================================================
    with tab5:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 👥 Audience Leads")
        st.markdown("People who have responded to your advertisements")
        
        # Demo lead submission
        with st.expander("📝 Demo: Submit a Test Lead", expanded=False):
            st.markdown("This simulates an audience member responding to your ad.")
            test_name = st.text_input("Name", "John Kamau", key="test_name")
            test_email = st.text_input("Email", "john@example.com", key="test_email")
            test_phone = st.text_input("Phone", "+254712345678", key="test_phone")
            test_interest = st.text_input("Interested Product", "Your Product/Service", key="test_interest")
            test_message = st.text_area("Message", "I saw your ad and I'm interested!", key="test_message")
            
            if st.button("Submit Test Lead", key="submit_test"):
                lead_id = add_audience_lead(company_id, 1, "Test Campaign", test_name, test_email, test_phone, test_interest, test_message, "Website")
                if lead_id:
                    st.success("Test lead submitted! Refresh to see it below.")
                    st.rerun()
                else:
                    st.error("Error submitting lead")
        
        st.markdown("---")
        
        if not leads_df.empty:
            st.markdown(f"#### Your Leads ({len(leads_df[leads_df['status'] == 'new'])} new)")
            
            for _, lead in leads_df.iterrows():
                if lead['status'] == 'new':
                    badge = '<span class="badge-new">NEW</span>'
                elif lead['status'] == 'contacted':
                    badge = '<span class="badge-contacted">CONTACTED</span>'
                else:
                    badge = '<span class="badge-converted">CONVERTED</span>'
                
                st.markdown(f"""
                <div class="lead-card">
                    <p><strong>{lead['lead_name']}</strong> {badge} - {lead['created_date'][:10] if lead['created_date'] else 'N/A'}</p>
                    <p><strong>Phone:</strong> {lead['lead_phone']} | <strong>Email:</strong> {lead['lead_email']}</p>
                    <p><strong>Interested in:</strong> {lead['interest_product']}</p>
                    <p><strong>Message:</strong> {lead['message'][:200] if lead['message'] else 'No message'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if lead['status'] == 'new':
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"📞 Mark Contacted", key=f"contact_{lead['lead_id']}"):
                            update_lead_status(lead['lead_id'], 'contacted')
                            st.rerun()
                    with col2:
                        if st.button(f"✅ Mark Converted", key=f"convert_{lead['lead_id']}"):
                            update_lead_status(lead['lead_id'], 'converted')
                            st.rerun()
                elif lead['status'] == 'contacted':
                    if st.button(f"✅ Mark Converted", key=f"convert_{lead['lead_id']}"):
                        update_lead_status(lead['lead_id'], 'converted')
                        st.rerun()
                
                st.markdown("---")
            
            # Lead statistics
            st.markdown("#### Lead Status Summary")
            status_counts = leads_df.groupby('status').size().reset_index(name='count')
            st.dataframe(status_counts, use_container_width=True, hide_index=True)
            
            csv = leads_df.to_csv(index=False)
            st.download_button("📥 Export Your Leads", csv, f"my_leads_{datetime.now().strftime('%Y%m%d')}.csv")
        else:
            st.info("No audience leads yet. Use the demo form above to test lead capture.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# MAIN APP ROUTING
# ============================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.show_booking_form = False
    st.session_state.selected_station = None
    st.session_state.recommended_stations = []

if st.session_state.logged_in:
    if st.session_state.role == 'admin':
        show_admin_dashboard()
    else:
        show_client_portal()
    
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.show_booking_form = False
            st.session_state.selected_station = None
            st.session_state.recommended_stations = []
            st.rerun()
else:
    show_login()

st.markdown("""
<div class="footer">
    <p>Ad Intelligence Kenya | AI-Powered Media Recommendations & Lead Generation</p>
</div>
""", unsafe_allow_html=True)
