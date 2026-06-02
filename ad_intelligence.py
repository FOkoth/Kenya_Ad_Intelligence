"""
Ad Intelligence Kenya - Complete Platform with Lead Generation
Features: Smart Recommendations + Client Booking + Two-Way Approval Workflow
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
    
    if 'campaign_goal' not in columns:
        cursor.execute("ALTER TABLE booking_requests ADD COLUMN campaign_goal TEXT")
    
    if 'status_updated_date' not in columns:
        cursor.execute("ALTER TABLE booking_requests ADD COLUMN status_updated_date TEXT")
    
    if 'admin_notes' not in columns:
        cursor.execute("ALTER TABLE booking_requests ADD COLUMN admin_notes TEXT")
    
    if 'approved_date' not in columns:
        cursor.execute("ALTER TABLE booking_requests ADD COLUMN approved_date TEXT")
    
    if 'confirmed_date' not in columns:
        cursor.execute("ALTER TABLE booking_requests ADD COLUMN confirmed_date TEXT")
    
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
    
    # Booking requests with approval workflow
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
        campaign_goal TEXT,
        contact_name TEXT,
        contact_email TEXT,
        contact_phone TEXT,
        status TEXT DEFAULT 'pending_approval',
        request_date TEXT,
        status_updated_date TEXT,
        approved_date TEXT,
        confirmed_date TEXT,
        admin_notes TEXT,
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
    
    .warning-card {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
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
    .booking-card-pending { border-left: 4px solid #F59E0B; }
    .booking-card-approved { border-left: 4px solid #8B5CF6; }
    .booking-card-confirmed { border-left: 4px solid #10B981; }
    .booking-card-suspended { border-left: 4px solid #EF4444; }
    
    .lead-card {
        background: #F0FDF4;
        border: 1px solid #86EFAC;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .badge-pending { background: #F59E0B; color: white; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
    .badge-approved { background: #8B5CF6; color: white; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
    .badge-confirmed { background: #10B981; color: white; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
    .badge-suspended { background: #EF4444; color: white; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
    .badge-new { background: #10B981; color: white; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
    
    .footer { text-align: center; padding: 1rem; margin-top: 1.5rem; background: #F8FAFC; border-radius: 12px; font-size: 0.7rem; color: #64748B; }
    
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
    
    .status-timeline {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.5rem 0;
        padding: 0.5rem;
        background: #F8FAFC;
        border-radius: 8px;
    }
    .status-step {
        flex: 1;
        text-align: center;
        font-size: 0.7rem;
    }
    .status-step-active { color: #004953; font-weight: bold; }
    .status-step-complete { color: #10B981; }
    .status-step-pending { color: #94A3B8; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATABASE HELPER FUNCTIONS
# ============================================================================
def get_company_data(company_id):
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
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        df = pd.read_sql_query("SELECT company_id, company_name, industry, email, phone FROM companies WHERE status = 'active'", conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

def get_company_logs(company_id):
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

def create_booking_request(company_id, selected_stations_list, campaign_goal, budget, duration, audience, region_type, contact_name, contact_email, contact_phone, notes=""):
    """Create a booking request from advertiser with multiple stations"""
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        cursor = conn.cursor()
        selected_stations_str = ", ".join(selected_stations_list)
        primary_station = selected_stations_list[0] if selected_stations_list else "Multiple"
        media_type = "Mixed"
        
        cursor.execute('''
        INSERT INTO booking_requests (
            company_id, station_name, selected_stations, media_type, preferred_time, 
            budget_kes, duration_days, target_audience, campaign_goal, 
            contact_name, contact_email, contact_phone, status, request_date, status_updated_date, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company_id, primary_station, selected_stations_str, media_type, datetime.now().strftime("%Y-%m-%d"),
            budget, duration, audience, campaign_goal,
            contact_name, contact_email, contact_phone, 'pending_approval', 
            datetime.now().isoformat(), datetime.now().isoformat(), notes
        ))
        booking_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return booking_id
    except Exception as e:
        print(f"Error creating booking: {e}")
        return None

def get_booking_requests(company_id=None):
    """Get all booking requests, optionally filtered by company"""
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        if company_id:
            df = pd.read_sql_query('''
                SELECT * FROM booking_requests 
                WHERE company_id = ? 
                ORDER BY request_date DESC
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

def update_booking_status(booking_id, status, admin_notes=None):
    """Update booking request status with timestamps"""
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        cursor = conn.cursor()
        
        current_time = datetime.now().isoformat()
        
        if status == 'approved':
            cursor.execute('''
                UPDATE booking_requests 
                SET status = ?, status_updated_date = ?, approved_date = ?, admin_notes = ?
                WHERE booking_id = ?
            ''', (status, current_time, current_time, admin_notes, booking_id))
        elif status == 'confirmed':
            cursor.execute('''
                UPDATE booking_requests 
                SET status = ?, status_updated_date = ?, confirmed_date = ?
                WHERE booking_id = ?
            ''', (status, current_time, current_time, booking_id))
        else:
            cursor.execute('''
                UPDATE booking_requests 
                SET status = ?, status_updated_date = ?
                WHERE booking_id = ?
            ''', (status, current_time, booking_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

def get_booking_statistics(company_id=None):
    """Get booking statistics for dashboard"""
    bookings_df = get_booking_requests(company_id)
    if bookings_df.empty:
        return {'total': 0, 'pending_approval': 0, 'approved': 0, 'confirmed': 0, 'suspended': 0}
    
    total = len(bookings_df)
    pending_approval = len(bookings_df[bookings_df['status'] == 'pending_approval'])
    approved = len(bookings_df[bookings_df['status'] == 'approved'])
    confirmed = len(bookings_df[bookings_df['status'] == 'confirmed'])
    suspended = len(bookings_df[bookings_df['status'] == 'suspended'])
    
    return {
        'total': total,
        'pending_approval': pending_approval,
        'approved': approved,
        'confirmed': confirmed,
        'suspended': suspended
    }

def add_audience_lead(company_id, campaign_id, station_name, name, email, phone, product_interest, message, source):
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

def get_audience_leads(company_id=None):
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        if company_id:
            df = pd.read_sql_query('''
                SELECT * FROM audience_leads 
                WHERE company_id = ? 
                ORDER BY created_date DESC
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

def get_lead_statistics(company_id=None):
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
# ADMIN DASHBOARD
# ============================================================================
def show_admin_dashboard():
    st.markdown("""
    <div class="main-header">
        <h1>Admin Dashboard</h1>
        <p>System-wide advertising intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    all_companies = get_all_companies()
    all_bookings = get_booking_requests()
    all_leads = get_audience_leads()
    
    # Statistics Row
    st.markdown("### 📊 Platform Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
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
            <div class="metric-label">📋 Total Bookings</div>
            <div class="metric-value">{total_bookings}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pending_approval = len(all_bookings[all_bookings['status'] == 'pending_approval']) if not all_bookings.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏳ Pending Approval</div>
            <div class="metric-value">{pending_approval}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        confirmed = len(all_bookings[all_bookings['status'] == 'confirmed']) if not all_bookings.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">✅ Confirmed</div>
            <div class="metric-value">{confirmed}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        total_leads = len(all_leads) if not all_leads.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">👥 Total Leads</div>
            <div class="metric-value">{total_leads}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for Admin
    admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs([
        "📊 Performance", "📋 Pending Approvals", "👥 All Leads", "🏢 Companies"
    ])
    
    # ========================================================================
    # ADMIN TAB 1: Performance
    # ========================================================================
    with admin_tab1:
        if not all_companies.empty:
            selected_company = st.selectbox("Select Company", ["All Companies"] + all_companies['company_name'].tolist())
            
            if selected_company != "All Companies":
                company_id = all_companies[all_companies['company_name'] == selected_company]['company_id'].values[0]
                df = get_company_data(company_id)
                lead_stats = get_lead_statistics(company_id)
                booking_stats = get_booking_statistics(company_id)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">👥 Leads</div><div class="metric-value">{lead_stats["total"]}</div></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">✅ Converted</div><div class="metric-value">{lead_stats["converted"]}</div></div>', unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">📋 Bookings</div><div class="metric-value">{booking_stats["total"]}</div></div>', unsafe_allow_html=True)
                with col4:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">⏳ Pending Approval</div><div class="metric-value">{booking_stats["pending_approval"]}</div></div>', unsafe_allow_html=True)
                
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
            else:
                st.info("Select a company to view detailed performance")
    
    # ========================================================================
    # ADMIN TAB 2: Pending Approvals
    # ========================================================================
    with admin_tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 📋 Booking Requests - Pending Approval")
        
        pending_bookings = all_bookings[all_bookings['status'] == 'pending_approval'] if not all_bookings.empty else pd.DataFrame()
        
        if not pending_bookings.empty:
            for _, booking in pending_bookings.iterrows():
                st.markdown(f"""
                <div class="booking-card booking-card-pending">
                    <p><strong>Booking #{booking['booking_id']}</strong> - {booking['request_date'][:10] if booking['request_date'] else 'N/A'}</p>
                    <p><strong>Company:</strong> {booking['company_name'] if 'company_name' in booking else 'N/A'}</p>
                    <p><strong>Stations:</strong> {booking.get('selected_stations', booking['station_name'])}</p>
                    <p><strong>Budget:</strong> KES {booking['budget_kes']:,.0f} | <strong>Duration:</strong> {booking['duration_days']} days</p>
                    <p><strong>Campaign Goal:</strong> {booking.get('campaign_goal', 'N/A')}</p>
                    <p><strong>Contact:</strong> {booking['contact_name']} - {booking['contact_email']} - {booking['contact_phone']}</p>
                    <p><strong>Status:</strong> <span class="badge-pending">PENDING APPROVAL</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    admin_notes = st.text_area(f"Admin Notes (Optional)", key=f"notes_{booking['booking_id']}", placeholder="Add any notes about this approval...")
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(f"✅ Approve Booking", key=f"approve_{booking['booking_id']}"):
                        update_booking_status(booking['booking_id'], 'approved', admin_notes if admin_notes else None)
                        st.success(f"Booking #{booking['booking_id']} approved! The client will now confirm.")
                        st.rerun()
                    
                    if st.button(f"❌ Reject / Suspend", key=f"suspend_{booking['booking_id']}"):
                        update_booking_status(booking['booking_id'], 'suspended', admin_notes if admin_notes else None)
                        st.warning(f"Booking #{booking['booking_id']} suspended.")
                        st.rerun()
                
                st.markdown("---")
        else:
            st.info("No pending approvals. All booking requests have been processed.")
        
        # Show approved but not yet confirmed bookings
        st.markdown("---")
        st.markdown("#### ✅ Approved - Awaiting Client Confirmation")
        
        approved_bookings = all_bookings[all_bookings['status'] == 'approved'] if not all_bookings.empty else pd.DataFrame()
        
        if not approved_bookings.empty:
            for _, booking in approved_bookings.iterrows():
                st.markdown(f"""
                <div class="booking-card booking-card-approved">
                    <p><strong>Booking #{booking['booking_id']}</strong> - Approved on {booking['approved_date'][:10] if booking.get('approved_date') else 'N/A'}</p>
                    <p><strong>Company:</strong> {booking['company_name'] if 'company_name' in booking else 'N/A'}</p>
                    <p><strong>Stations:</strong> {booking.get('selected_stations', booking['station_name'])}</p>
                    <p><strong>Budget:</strong> KES {booking['budget_kes']:,.0f}</p>
                    <p><strong>Status:</strong> <span class="badge-approved">APPROVED - AWAITING CLIENT CONFIRMATION</span></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No approved bookings awaiting confirmation.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # ADMIN TAB 3: All Leads
    # ========================================================================
    with admin_tab3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 👥 All Audience Leads")
        
        if not all_leads.empty:
            status_filter = st.selectbox("Filter by Status", ["All", "New", "Contacted", "Converted"], key="admin_lead_filter")
            
            filtered_leads = all_leads
            if status_filter != "All":
                filtered_leads = all_leads[all_leads['status'] == status_filter.lower()]
            
            for _, lead in filtered_leads.iterrows():
                badge = "badge-new" if lead['status'] == 'new' else "badge-pending" if lead['status'] == 'contacted' else "badge-confirmed"
                
                st.markdown(f"""
                <div class="lead-card">
                    <p><strong>{lead['lead_name']}</strong> <span class="{badge}">{lead['status'].upper()}</span> - {lead['created_date'][:10] if lead['created_date'] else 'N/A'}</p>
                    <p><strong>Company:</strong> {lead['company_name']} | <strong>Phone:</strong> {lead['lead_phone']} | <strong>Email:</strong> {lead['lead_email']}</p>
                    <p><strong>Interested in:</strong> {lead['interest_product']}</p>
                    <p><strong>Message:</strong> {lead['message'][:200] if lead['message'] else 'No message'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if lead['status'] == 'new':
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"📞 Mark Contacted", key=f"admin_contact_{lead['lead_id']}"):
                            update_lead_status(lead['lead_id'], 'contacted')
                            st.rerun()
                    with col2:
                        if st.button(f"✅ Mark Converted", key=f"admin_convert_{lead['lead_id']}"):
                            update_lead_status(lead['lead_id'], 'converted')
                            st.rerun()
                elif lead['status'] == 'contacted':
                    if st.button(f"✅ Mark Converted", key=f"admin_convert_{lead['lead_id']}"):
                        update_lead_status(lead['lead_id'], 'converted')
                        st.rerun()
                
                st.markdown("---")
            
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
        conn.close()
    except Exception as e:
        company_name = "Your Company"
    
    st.markdown(f"""
    <div class="main-header">
        <h1>Welcome, {company_name}</h1>
        <p>Your personalized advertising intelligence dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get statistics
    lead_stats = get_lead_statistics(company_id)
    booking_stats = get_booking_statistics(company_id)
    
    # Lead Metrics Row
    st.markdown("### 📊 Your Performance Overview")
    
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
            <div class="metric-label">✅ Converted</div>
            <div class="metric-value">{lead_stats['converted']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📋 Total Bookings</div>
            <div class="metric-value">{booking_stats['total']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏳ Pending Approval</div>
            <div class="metric-value">{booking_stats['pending_approval']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    df = get_company_data(company_id)
    logs_df = get_company_logs(company_id)
    bookings_df = get_booking_requests(company_id)
    leads_df = get_audience_leads(company_id)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Performance", "🎯 Smart Recommendations", "📺 TV/Radio Logs", "📋 My Bookings", "👥 Audience Leads"
    ])
    
    # ========================================================================
    # TAB 1: Performance
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
        else:
            st.info("No campaign data available")
    
    # ========================================================================
    # TAB 2: Smart Recommendations
    # ========================================================================
    with tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 🎯 AI-Powered Media Recommendation Engine")
        
        engine = MediaRecommendationEngine()
        station_db = StationDatabase()
        
        if 'generated_recommendations' not in st.session_state:
            st.session_state.generated_recommendations = None
        if 'campaign_params' not in st.session_state:
            st.session_state.campaign_params = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_goal = st.selectbox("Campaign Goal", ["Brand Awareness", "Lead Generation", "Sales", "Customer Retention", "Product Launch"])
            budget = st.number_input("Total Budget (KES)", min_value=100000, max_value=10000000, value=500000, step=50000)
            duration = st.select_slider("Campaign Duration (Days)", options=[7, 14, 21, 30, 45, 60], value=14)
        
        with col2:
            target_audience = st.selectbox("Target Audience", ["Mass Market", "Youth (18-35)", "Professionals (25-45)", "Rural Population", "Urban Consumers", "Affluent Segment"])
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
            
            st.session_state.generated_recommendations = recommendations
            st.session_state.campaign_params = {
                'goal': campaign_goal,
                'budget': budget,
                'duration': duration,
                'audience': target_audience,
                'region': region_type
            }
            st.rerun()
        
        if st.session_state.generated_recommendations:
            recommendations = st.session_state.generated_recommendations
            params = st.session_state.campaign_params
            
            estimated_roas = 2.5
            
            st.markdown("---")
            st.markdown(f"""
            <div class="success-card">
                <h4 style="margin:0 0 0.5rem 0;">📈 Estimated Campaign Performance</h4>
                <p style="font-size:1.5rem; margin:0;"><strong>Estimated ROAS: {estimated_roas}x</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🏆 Recommended Stations")
            
            for idx, rec in enumerate(recommendations[:5]):
                price_icon = "🟢" if rec["price_tier"] == "Economy" else "🟡" if rec["price_tier"] == "Standard" else "🔴"
                st.markdown(f"""
                <div class="rec-card">
                    <h4>#{idx+1} {rec['station_name']} ({rec['media_type']}) {price_icon} {rec['price_tier']}</h4>
                    <p><strong>📊 Reach:</strong> {rec['reach']:,} | <strong>💰 Cost per spot:</strong> KES {rec['cost_per_spot']:,}</p>
                    <p><strong>📺 Recommended Spots:</strong> {rec['recommended_spots']} per day</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 📞 Book Your Campaign")
            
            station_options = [f"{r['station_name']} ({r['media_type']})" for r in recommendations[:5]]
            st.markdown("**Select stations to book:**")
            
            selected_stations = []
            for station in station_options:
                if st.checkbox(station, key=f"station_check_{station}"):
                    selected_stations.append(station)
            
            if selected_stations:
                st.markdown("---")
                st.markdown("#### Complete Your Booking")
                
                with st.form(key="booking_submission_form"):
                    st.markdown("##### Contact Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        contact_name = st.text_input("Your Name*", key="booking_name")
                        contact_email = st.text_input("Email Address*", key="booking_email")
                    with col2:
                        contact_phone = st.text_input("Phone Number*", key="booking_phone")
                        preferred_launch = st.date_input("Preferred Launch Date", min_value=datetime.now().date(), key="booking_date")
                    
                    additional_notes = st.text_area("Campaign Details / Special Requirements", key="booking_notes")
                    
                    submit_button = st.form_submit_button("📞 Submit Booking Request", use_container_width=True)
                    
                    if submit_button:
                        if contact_name and contact_email and contact_phone:
                            booking_id = create_booking_request(
                                company_id, selected_stations, params['goal'],
                                params['budget'], params['duration'], params['audience'], params['region'],
                                contact_name, contact_email, contact_phone,
                                additional_notes
                            )
                            if booking_id:
                                st.success(f"✅ Booking request submitted! Reference: #{booking_id}")
                                st.balloons()
                                st.info("Your request is now pending admin approval. You will be notified once approved.")
                                st.session_state.generated_recommendations = None
                                st.rerun()
                            else:
                                st.error("Error submitting request. Please try again.")
                        else:
                            st.error("Please fill in all contact fields")
            else:
                st.info("👆 Select at least one station above to continue with booking")
        
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
        else:
            st.info("No airtime logs yet")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 4: My Bookings (Client View with Approval Workflow)
    # ========================================================================
    with tab4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 📋 My Booking Requests")
        
        if not bookings_df.empty:
            # Booking statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total", booking_stats['total'])
            with col2:
                st.metric("Pending Approval", booking_stats['pending_approval'])
            with col3:
                st.metric("Approved", booking_stats['approved'])
            with col4:
                st.metric("Confirmed", booking_stats['confirmed'])
            
            st.markdown("---")
            
            for _, booking in bookings_df.iterrows():
                # Determine border and badge based on status
                if booking['status'] == 'pending_approval':
                    border_class = "booking-card-pending"
                    status_badge = "badge-pending"
                    status_text = "PENDING APPROVAL"
                elif booking['status'] == 'approved':
                    border_class = "booking-card-approved"
                    status_badge = "badge-approved"
                    status_text = "APPROVED - READY FOR CONFIRMATION"
                elif booking['status'] == 'confirmed':
                    border_class = "booking-card-confirmed"
                    status_badge = "badge-confirmed"
                    status_text = "CONFIRMED"
                else:
                    border_class = "booking-card-suspended"
                    status_badge = "badge-suspended"
                    status_text = "SUSPENDED"
                
                st.markdown(f"""
                <div class="booking-card {border_class}">
                    <p><strong>Booking #{booking['booking_id']}</strong> - {booking['request_date'][:10] if booking['request_date'] else 'N/A'}</p>
                    <p><strong>Stations:</strong> {booking.get('selected_stations', booking['station_name'])}</p>
                    <p><strong>Budget:</strong> KES {booking['budget_kes']:,.0f} | <strong>Duration:</strong> {booking['duration_days']} days</p>
                    <p><strong>Campaign Goal:</strong> {booking.get('campaign_goal', 'N/A')}</p>
                    <p><strong>Status:</strong> <span class="{status_badge}">{status_text}</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show approval timeline
                st.markdown("**Approval Status:**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if booking['status'] != 'pending_approval':
                        st.markdown("✅ **Request Submitted**")
                    else:
                        st.markdown("⏳ **Request Submitted**")
                    st.caption(booking['request_date'][:10] if booking['request_date'] else 'N/A')
                
                with col2:
                    if booking['status'] in ['approved', 'confirmed']:
                        st.markdown("✅ **Admin Approved**")
                        st.caption(booking['approved_date'][:10] if booking.get('approved_date') else 'N/A')
                    elif booking['status'] == 'pending_approval':
                        st.markdown("⏳ **Pending Approval**")
                        st.caption("Waiting for admin")
                    else:
                        st.markdown("❌ **Not Approved**")
                
                with col3:
                    if booking['status'] == 'confirmed':
                        st.markdown("✅ **Client Confirmed**")
                        st.caption(booking['confirmed_date'][:10] if booking.get('confirmed_date') else 'N/A')
                    elif booking['status'] == 'approved':
                        st.markdown("⚠️ **Awaiting Your Confirmation**")
                        st.caption("Ready to confirm")
                    else:
                        st.markdown("⏳ **Pending**")
                
                # Action buttons based on status
                if booking['status'] == 'approved':
                    st.markdown("---")
                    st.markdown("#### ✅ Your booking has been approved by admin!")
                    st.markdown("Please confirm to proceed with your campaign.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ Confirm This Booking", key=f"confirm_{booking['booking_id']}"):
                            update_booking_status(booking['booking_id'], 'confirmed')
                            st.success("Booking confirmed! Your campaign will now be scheduled.")
                            st.rerun()
                    with col2:
                        if st.button(f"⏸️ Suspend Instead", key=f"suspend_{booking['booking_id']}"):
                            update_booking_status(booking['booking_id'], 'suspended')
                            st.warning("Booking suspended. Contact admin for reactivation.")
                            st.rerun()
                
                elif booking['status'] == 'pending_approval':
                    st.markdown("---")
                    st.info("⏳ Your booking is pending admin approval. You will be notified once approved.")
                
                elif booking['status'] == 'confirmed':
                    st.markdown("---")
                    st.success("✅ Your booking is confirmed! Our team will contact you shortly to finalize the campaign schedule.")
                    
                    if st.button(f"📞 Request Changes", key=f"request_change_{booking['booking_id']}"):
                        st.info("Please contact our support team at support@adintelkenya.com to request changes.")
                
                st.markdown("---")
        else:
            st.info("No booking requests yet. Generate a media plan in the Smart Recommendations tab to create your first booking.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 5: Audience Leads
    # ========================================================================
    with tab5:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 👥 Audience Leads")
        
        with st.expander("📝 Demo: Submit a Test Lead", expanded=False):
            test_name = st.text_input("Name", "John Kamau", key="test_name")
            test_email = st.text_input("Email", "john@example.com", key="test_email")
            test_phone = st.text_input("Phone", "+254712345678", key="test_phone")
            test_interest = st.text_input("Interested Product", "Your Product/Service", key="test_interest")
            test_message = st.text_area("Message", "I saw your ad and I'm interested!", key="test_message")
            
            if st.button("Submit Test Lead", key="submit_test"):
                lead_id = add_audience_lead(company_id, 1, "Test Campaign", test_name, test_email, test_phone, test_interest, test_message, "Website")
                if lead_id:
                    st.success("Test lead submitted!")
                    st.rerun()
        
        st.markdown("---")
        
        if not leads_df.empty:
            st.markdown(f"#### Your Leads ({len(leads_df[leads_df['status'] == 'new'])} new)")
            
            for _, lead in leads_df.iterrows():
                badge = "badge-new" if lead['status'] == 'new' else "badge-pending" if lead['status'] == 'contacted' else "badge-confirmed"
                
                st.markdown(f"""
                <div class="lead-card">
                    <p><strong>{lead['lead_name']}</strong> <span class="{badge}">{lead['status'].upper()}</span> - {lead['created_date'][:10] if lead['created_date'] else 'N/A'}</p>
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
            
            st.markdown("#### Lead Status Summary")
            status_counts = leads_df.groupby('status').size().reset_index(name='count')
            st.dataframe(status_counts, use_container_width=True, hide_index=True)
            
            csv = leads_df.to_csv(index=False)
            st.download_button("📥 Export Your Leads", csv, f"my_leads_{datetime.now().strftime('%Y%m%d')}.csv")
        else:
            st.info("No audience leads yet")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# MAIN APP ROUTING
# ============================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.generated_recommendations = None
    st.session_state.campaign_params = {}

if st.session_state.logged_in:
    if st.session_state.role == 'admin':
        show_admin_dashboard()
    else:
        show_client_portal()
    
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.generated_recommendations = None
            st.session_state.campaign_params = {}
            st.rerun()
else:
    show_login()

st.markdown("""
<div class="footer">
    <p>Ad Intelligence Kenya | AI-Powered Media Recommendations & Two-Way Approval Workflow</p>
</div>
""", unsafe_allow_html=True)
