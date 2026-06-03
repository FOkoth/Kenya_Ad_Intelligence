"""
Ad Intelligence Kenya - Complete Platform with Phase 1 Features
Includes: Email Notifications, Downloadable Charts, Lead Scoring, Station Contacts, Loading Animations
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
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import io
import base64

# ============================================================================
# EMAIL CONFIGURATION (Update with your SMTP settings)
# ============================================================================
# For demo purposes, we'll create a placeholder. In production, configure your SMTP.
# For now, notifications will be shown in-app. To enable email, uncomment and configure below.

SMTP_CONFIG = {
    'enabled': False,  # Set to True to enable email notifications
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your-email@gmail.com',
    'sender_password': 'your-app-password'  # Use App Password for Gmail
}

def send_email_notification(recipient_email, subject, body):
    """Send email notification (placeholder - will show in-app if not configured)"""
    if not SMTP_CONFIG['enabled'] or not recipient_email:
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_CONFIG['sender_email']
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_CONFIG['smtp_server'], SMTP_CONFIG['smtp_port']) as server:
            server.starttls(context=context)
            server.login(SMTP_CONFIG['sender_email'], SMTP_CONFIG['sender_password'])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

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
    
    # Check and add missing columns to audience_leads (Lead Scoring)
    cursor.execute("PRAGMA table_info(audience_leads)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'assigned_to' not in columns:
        cursor.execute("ALTER TABLE audience_leads ADD COLUMN assigned_to TEXT")
    
    if 'converted_date' not in columns:
        cursor.execute("ALTER TABLE audience_leads ADD COLUMN converted_date TEXT")
    
    if 'lead_score' not in columns:
        cursor.execute("ALTER TABLE audience_leads ADD COLUMN lead_score TEXT DEFAULT 'warm'")
    
    if 'last_contacted' not in columns:
        cursor.execute("ALTER TABLE audience_leads ADD COLUMN last_contacted TEXT")
    
    # Check and add missing columns to stations (Contact Details)
    cursor.execute("PRAGMA table_info(stations)")
    if cursor.fetchone() is None:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stations (
            station_id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_name TEXT UNIQUE,
            media_type TEXT,
            region TEXT,
            contact_person TEXT,
            contact_phone TEXT,
            contact_email TEXT,
            address TEXT,
            website TEXT
        )
        ''')
        
        # Insert station contact details
        station_contacts = [
            ('Citizen TV', 'TV', 'National', 'John Mwangi', '+254720123456', 'sales@citizen.co.ke', 'P.O. Box 12345, Nairobi', 'www.citizen.co.ke'),
            ('KTN', 'TV', 'National', 'Sarah Wanjiku', '+254721234567', 'adverts@ktnkenya.co.ke', 'P.O. Box 12346, Nairobi', 'www.ktnkenya.co.ke'),
            ('NTV', 'TV', 'National', 'Peter Omondi', '+254722345678', 'sales@ntv.co.ke', 'P.O. Box 12347, Nairobi', 'www.ntv.co.ke'),
            ('Citizen Radio', 'Radio', 'National', 'James Kariuki', '+254723456789', 'radio@citizen.co.ke', 'P.O. Box 12348, Nairobi', 'www.citizen.co.ke/radio'),
            ('Radio Jambo', 'Radio', 'National', 'Grace Muthoni', '+254724567890', 'jambo@royalmedia.co.ke', 'P.O. Box 12349, Nairobi', 'www.radiojambo.co.ke'),
            ('Classic 105', 'Radio', 'National', 'Michael Otieno', '+254725678901', 'classic@classic105.co.ke', 'P.O. Box 12350, Nairobi', 'www.classic105.co.ke'),
            ('Baraka FM', 'Radio', 'Coast', 'Fatma Hassan', '+254726789012', 'baraka@barakafm.co.ke', 'P.O. Box 12351, Mombasa', 'www.barakafm.co.ke'),
            ('Ramogi FM', 'Radio', 'Western', 'George Ochieng', '+254727890123', 'ramogi@ramogifm.co.ke', 'P.O. Box 12352, Kisumu', 'www.ramogifm.co.ke'),
                        ('Inooro FM', 'Radio', 'Central', 'Jane Wambui', '+254728901234', 'inooro@royalmedia.co.ke', 'P.O. Box 12353, Nyeri', 'www.inoorofm.co.ke'),
            ('Kameme FM', 'Radio', 'Central', 'David Maina', '+254729012345', 'kameme@kamemefm.co.ke', 'P.O. Box 12354, Murang\'a', 'www.kamemefm.co.ke'),
        ]
        
        for station in station_contacts:
            cursor.execute('''
            INSERT OR IGNORE INTO stations (station_name, media_type, region, contact_person, contact_phone, contact_email, address, website)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', station)
    
    conn.commit()
    conn.close()

# ============================================================================
# HELPER FUNCTIONS FOR DOWNLOADABLE CHARTS
# ============================================================================
def get_image_download_link(fig, filename="chart.png"):
    """Generate a download link for a plotly chart"""
    img_bytes = fig.to_image(format="png", width=800, height=500, scale=2)
    b64 = base64.b64encode(img_bytes).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">📥 Download as PNG</a>'
    return href

def fig_to_png(fig, filename="chart.png"):
    """Convert plotly figure to PNG and return download button"""
    img_bytes = fig.to_image(format="png", width=800, height=500, scale=2)
    b64 = base64.b64encode(img_bytes).decode()
    return b64

# ============================================================================
# LEAD SCORING FUNCTION
# ============================================================================
def calculate_lead_score(lead, messages=None):
    """Calculate lead score based on engagement and interest"""
    score = 0
    score_reasons = []
    
    # Check message content for interest signals
    message = lead.get('message', '').lower() if isinstance(lead, dict) else ''
    
    if 'interested' in message or 'buy' in message or 'purchase' in message:
        score += 30
        score_reasons.append("High purchase intent")
    
    if 'price' in message or 'cost' in message or 'how much' in message:
        score += 20
        score_reasons.append("Price inquiry - strong interest")
    
    if 'when' in message or 'available' in message or 'get' in message:
        score += 15
        score_reasons.append("Timing/availability question")
    
    if len(message) > 50:
        score += 10
        score_reasons.append("Detailed message")
    
    # Lead status scoring
    status = lead.get('status', 'new') if isinstance(lead, dict) else 'new'
    if status == 'converted':
        score += 50
        score_reasons.append("Already converted")
    elif status == 'contacted':
        score += 20
        score_reasons.append("Contacted - following up")
    
    # Determine lead score category
    if score >= 60:
        lead_score = "hot"
    elif score >= 30:
        lead_score = "warm"
    else:
        lead_score = "cold"
    
    return lead_score, score, score_reasons

# ============================================================================
# DATABASE HELPER FUNCTIONS (Continued)
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
    
    # Audience leads with lead scoring
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
        lead_score TEXT DEFAULT 'warm',
        assigned_to TEXT,
        converted_date TEXT,
        last_contacted TEXT,
        FOREIGN KEY (company_id) REFERENCES companies (company_id)
    )
    ''')
    
    # Stations table with contact details
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stations (
        station_id INTEGER PRIMARY KEY AUTOINCREMENT,
        station_name TEXT UNIQUE,
        media_type TEXT,
        region TEXT,
        contact_person TEXT,
        contact_phone TEXT,
        contact_email TEXT,
        address TEXT,
        website TEXT
    )
    ''')
    
    # Insert station contact details if empty
    cursor.execute("SELECT COUNT(*) FROM stations")
    if cursor.fetchone()[0] == 0:
        station_contacts = [
            ('Citizen TV', 'TV', 'National', 'John Mwangi', '+254720123456', 'sales@citizen.co.ke', 'P.O. Box 12345, Nairobi', 'www.citizen.co.ke'),
            ('KTN', 'TV', 'National', 'Sarah Wanjiku', '+254721234567', 'adverts@ktnkenya.co.ke', 'P.O. Box 12346, Nairobi', 'www.ktnkenya.co.ke'),
            ('NTV', 'TV', 'National', 'Peter Omondi', '+254722345678', 'sales@ntv.co.ke', 'P.O. Box 12347, Nairobi', 'www.ntv.co.ke'),
            ('KBC', 'TV', 'National', 'James Kariuki', '+254723456789', 'advertising@kbc.co.ke', 'P.O. Box 12348, Nairobi', 'www.kbc.co.ke'),
            ('Citizen Radio', 'Radio', 'National', 'Grace Muthoni', '+254724567890', 'radio@citizen.co.ke', 'P.O. Box 12349, Nairobi', 'www.citizen.co.ke/radio'),
            ('Radio Jambo', 'Radio', 'National', 'Michael Otieno', '+254725678901', 'jambo@royalmedia.co.ke', 'P.O. Box 12350, Nairobi', 'www.radiojambo.co.ke'),
            ('Classic 105', 'Radio', 'National', 'Wanjiku Kimani', '+254726789012', 'classic@classic105.co.ke', 'P.O. Box 12351, Nairobi', 'www.classic105.co.ke'),
            ('Baraka FM', 'Radio', 'Coast', 'Fatma Hassan', '+254727890123', 'baraka@barakafm.co.ke', 'P.O. Box 12352, Mombasa', 'www.barakafm.co.ke'),
            ('Ramogi FM', 'Radio', 'Western', 'George Ochieng', '+254728901234', 'ramogi@ramogifm.co.ke', 'P.O. Box 12353, Kisumu', 'www.ramogifm.co.ke'),
            ('Inooro FM', 'Radio', 'Central', 'Jane Wambui', '+254729012345', 'inooro@royalmedia.co.ke', 'P.O. Box 12354, Nyeri', 'www.inoorofm.co.ke'),
            ('Kameme FM', 'Radio', 'Central', 'David Maina', '+254730123456', 'kameme@kamemefm.co.ke', 'P.O. Box 12355, Murang\'a', 'www.kamemefm.co.ke'),
            ('Milele FM', 'Radio', 'Coast', 'Hassan Omar', '+254731234567', 'milele@milelefm.co.ke', 'P.O. Box 12356, Mombasa', 'www.milelefm.co.ke'),
            ('Lake Victoria FM', 'Radio', 'Western', 'Thomas Omondi', '+254732345678', 'lakevictoria@lakeradio.co.ke', 'P.O. Box 12357, Kisumu', 'www.lakevictoriafm.co.ke'),
        ]
        
        for station in station_contacts:
            cursor.execute('''
            INSERT OR IGNORE INTO stations (station_name, media_type, region, contact_person, contact_phone, contact_email, address, website)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', station)
    
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
            
            # Generate sample leads with scoring
            sample_leads = [
                ("John Kamau", "john@example.com", "+254712345678", "Data Bundles", "I am very interested in your data bundles. Please call me to discuss pricing.", "Website", "hot"),
                ("Mary Wanjiku", "mary@example.com", "+254723456789", "M-Pesa Services", "What are your current rates for M-Pesa services?", "Facebook", "warm"),
                ("Peter Omondi", "peter@example.com", "+254734567890", "Home Internet", "Just browsing, might be interested later", "Instagram", "cold"),
                ("Sarah Mwangi", "sarah@example.com", "+254745678901", "Business Data", "I want to purchase the business data package. Please call me urgently!", "Website", "hot"),
            ]
            for lead in sample_leads:
                cursor.execute('''
                INSERT INTO audience_leads (company_id, lead_name, lead_email, lead_phone, interest_product, message, source, created_date, status, lead_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (company_id, lead[0], lead[1], lead[2], lead[3], lead[4], lead[5], datetime.now().isoformat(), 'new', lead[6]))
    
    conn.commit()
    conn.close()
    return True

# Run database initialization and migration
init_database()
migrate_database()

# ============================================================================
# CUSTOM CSS WITH LOADING ANIMATIONS
# ============================================================================
st.markdown("""
<style>
    /* Loading Animation */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loader {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #004953;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    .loading-text {
        text-align: center;
        color: #004953;
        font-size: 14px;
        margin-top: 10px;
    }
    
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #004953 0%, #006B7A 100%);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.75rem; }
    .main-header p { color: rgba(255,255,255,0.85); margin: 0.25rem 0 0 0; }
    
    /* Metric cards */
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
    
    /* Section cards */
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
    
    /* Recommendation cards */
    .rec-card {
        background: linear-gradient(135deg, #004953 0%, #003540 100%);
        border-radius: 12px;
        padding: 1rem;
        color: white;
        margin-bottom: 0.5rem;
    }
    .rec-card h4 { color: #C6A43F; margin: 0 0 0.5rem 0; font-size: 0.9rem; }
    .rec-card p { margin: 0.25rem 0; font-size: 0.8rem; }
    
    /* Lead scoring badges */
    .lead-hot { background: #EF4444; color: white; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
    .lead-warm { background: #F59E0B; color: white; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
    .lead-cold { background: #94A3B8; color: white; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
    
    /* Booking cards */
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
    
    /* Status badges */
    .badge-pending { background: #F59E0B; color: white; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
    .badge-approved { background: #8B5CF6; color: white; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
    .badge-confirmed { background: #10B981; color: white; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
    .badge-suspended { background: #EF4444; color: white; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
    .badge-new { background: #10B981; color: white; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; display: inline-block; }
    
    /* Station contact card */
    .station-contact-card {
        background: #F8FAFC;
        padding: 0.75rem;
        border-radius: 8px;
        margin-top: 0.5rem;
        font-size: 0.75rem;
    }
    
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
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOADING ANIMATION
# ============================================================================
def show_loading(message="Processing..."):
    """Display a loading animation"""
    loading_html = f"""
    <div class="loader"></div>
    <div class="loading-text">{message}</div>
    """
    return st.markdown(loading_html, unsafe_allow_html=True)

# ============================================================================
# DATABASE HELPER FUNCTIONS
# ============================================================================
def get_station_contacts(station_name):
    """Get contact details for a station"""
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        cursor = conn.cursor()
        cursor.execute("SELECT contact_person, contact_phone, contact_email, address, website FROM stations WHERE station_name = ?", (station_name,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                'contact_person': result[0],
                'contact_phone': result[1],
                'contact_email': result[2],
                'address': result[3],
                'website': result[4]
            }
        return None
    except Exception as e:
        return None

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
        
        # Send email notification to admin
        if contact_email:
            subject = f"New Booking Request #{booking_id} - Pending Approval"
            body = f"""
            <h2>New Booking Request</h2>
            <p><strong>Booking ID:</strong> #{booking_id}</p>
            <p><strong>Company:</strong> {contact_name}</p>
            <p><strong>Stations:</strong> {selected_stations_str}</p>
            <p><strong>Budget:</strong> KES {budget:,.0f}</p>
            <p><strong>Duration:</strong> {duration} days</p>
            <p><strong>Contact Email:</strong> {contact_email}</p>
            <p><strong>Contact Phone:</strong> {contact_phone}</p>
            <p>Please log in to the admin dashboard to approve or reject this request.</p>
            """
            send_email_notification("admin@adintelkenya.com", subject, body)
        
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
    """Update booking request status with timestamps and email notification"""
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        cursor = conn.cursor()
        
        # Get booking details for email
        cursor.execute("SELECT contact_email, contact_name, company_id FROM booking_requests WHERE booking_id = ?", (booking_id,))
        booking = cursor.fetchone()
        
        current_time = datetime.now().isoformat()
        
        if status == 'approved':
            cursor.execute('''
                UPDATE booking_requests 
                SET status = ?, status_updated_date = ?, approved_date = ?, admin_notes = ?
                WHERE booking_id = ?
            ''', (status, current_time, current_time, admin_notes, booking_id))
            
            # Send email notification to client
            if booking and booking[0]:
                subject = f"Booking #{booking_id} Has Been Approved!"
                body = f"""
                <h2>Great News! Your Booking Has Been Approved</h2>
                <p><strong>Booking ID:</strong> #{booking_id}</p>
                <p>Your booking request has been reviewed and approved by our team.</p>
                <p><strong>Next Steps:</strong></p>
                <ol>
                    <li>Log in to your dashboard</li>
                    <li>Go to "My Bookings" tab</li>
                    <li>Click "Confirm Booking" to proceed</li>
                </ol>
                <p>If you have any questions, please reply to this email.</p>
                """
                send_email_notification(booking[0], subject, body)
                
        elif status == 'confirmed':
            cursor.execute('''
                UPDATE booking_requests 
                SET status = ?, status_updated_date = ?, confirmed_date = ?
                WHERE booking_id = ?
            ''', (status, current_time, current_time, booking_id))
            
            # Send confirmation email
            if booking and booking[0]:
                subject = f"Booking #{booking_id} Confirmed!"
                body = f"""
                <h2>Booking Confirmed!</h2>
                <p><strong>Booking ID:</strong> #{booking_id}</p>
                <p>Your booking has been confirmed. Our team will contact you within 24 hours to finalize the campaign schedule.</p>
                <p>Thank you for choosing Ad Intelligence Kenya!</p>
                """
                send_email_notification(booking[0], subject, body)
                
        elif status == 'suspended':
            cursor.execute('''
                UPDATE booking_requests 
                SET status = ?, status_updated_date = ?, admin_notes = ?
                WHERE booking_id = ?
            ''', (status, current_time, admin_notes, booking_id))
            
            # Send suspension notice
            if booking and booking[0]:
                subject = f"Update on Booking #{booking_id}"
                body = f"""
                <h2>Booking Status Update</h2>
                <p><strong>Booking ID:</strong> #{booking_id}</p>
                <p>Your booking request has been suspended.</p>
                <p><strong>Reason:</strong> {admin_notes if admin_notes else 'Please contact support for more information.'}</p>
                <p>Please contact us to resolve any issues and reactivate your booking.</p>
                """
                send_email_notification(booking[0], subject, body)
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
        print(f"Error updating booking: {e}")
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
    """Add a lead from audience responding to ad with auto-scoring"""
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        cursor = conn.cursor()
        
        # Calculate lead score based on message
        lead_data = {'message': message, 'status': 'new'}
        lead_score, score_value, score_reasons = calculate_lead_score(lead_data)
        
        cursor.execute('''
        INSERT INTO audience_leads (company_id, campaign_id, station_name, lead_name, lead_email, lead_phone, interest_product, message, source, created_date, status, lead_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (company_id, campaign_id, station_name, name, email, phone, product_interest, message, source, datetime.now().isoformat(), 'new', lead_score))
        lead_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Send email notification to company
        conn2 = sqlite3.connect('ad_intelligence.db')
        cursor2 = conn2.cursor()
        cursor2.execute("SELECT email, company_name FROM companies WHERE company_id = ?", (company_id,))
        company = cursor2.fetchone()
        conn2.close()
        
        if company and company[0]:
            subject = f"New Lead: {name} interested in {product_interest}"
            body = f"""
            <h2>New Lead Generated</h2>
            <p><strong>Lead Score:</strong> {lead_score.upper()} ({score_value} points)</p>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Phone:</strong> {phone}</p>
            <p><strong>Interest:</strong> {product_interest}</p>
            <p><strong>Message:</strong> {message}</p>
            <p><strong>Source:</strong> {source}</p>
            <hr>
            <p>Log in to your dashboard to manage this lead.</p>
            """
            send_email_notification(company[0], subject, body)
        
        return lead_id
    except Exception as e:
        print(f"Error adding lead: {e}")
        return None

def get_audience_leads(company_id=None):
    try:
        conn = sqlite3.connect('ad_intelligence.db')
        if company_id:
            df = pd.read_sql_query('''
                SELECT * FROM audience_leads 
                WHERE company_id = ? 
                ORDER BY 
                    CASE lead_score 
                        WHEN 'hot' THEN 1 
                        WHEN 'warm' THEN 2 
                        WHEN 'cold' THEN 3 
                    END,
                    created_date DESC
            ''', conn, params=(company_id,))
        else:
            df = pd.read_sql_query('''
                SELECT al.*, c.company_name 
                FROM audience_leads al
                JOIN companies c ON al.company_id = c.company_id
                ORDER BY 
                    CASE al.lead_score 
                        WHEN 'hot' THEN 1 
                        WHEN 'warm' THEN 2 
                        WHEN 'cold' THEN 3 
                    END,
                    al.created_date DESC
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
        cursor.execute("UPDATE audience_leads SET status = ?, converted_date = ?, last_contacted = ? WHERE lead_id = ?", 
                      (status, converted_date, datetime.now().isoformat(), lead_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

def get_lead_statistics(company_id=None):
    leads_df = get_audience_leads(company_id)
    if leads_df.empty:
        return {'total': 0, 'new': 0, 'contacted': 0, 'converted': 0, 'conversion_rate': 0, 'hot': 0, 'warm': 0, 'cold': 0}
    
    total = len(leads_df)
    new = len(leads_df[leads_df['status'] == 'new'])
    contacted = len(leads_df[leads_df['status'] == 'contacted'])
    converted = len(leads_df[leads_df['status'] == 'converted'])
    hot = len(leads_df[leads_df['lead_score'] == 'hot'])
    warm = len(leads_df[leads_df['lead_score'] == 'warm'])
    cold = len(leads_df[leads_df['lead_score'] == 'cold'])
    conversion_rate = (converted / total * 100) if total > 0 else 0
    
    return {
        'total': total,
        'new': new,
        'contacted': contacted,
        'converted': converted,
        'conversion_rate': round(conversion_rate, 1),
        'hot': hot,
        'warm': warm,
        'cold': cold
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
                "Inooro FM": {"region": "Central", "reach": 1200000, "cost_per_spot": 45000, "primary_audience": ["Kikuyu Community"], "best_for": ["Agriculture"], "price_tier": "Standard"},
                "Kameme FM": {"region": "Central", "reach": 1000000, "cost_per_spot": 40000, "primary_audience": ["Kikuyu Community"], "best_for": ["Agriculture", "Real Estate"], "price_tier": "Standard"},
                "Milele FM": {"region": "Coast", "reach": 450000, "cost_per_spot": 35000, "primary_audience": ["Youth"], "best_for": ["Entertainment"], "price_tier": "Economy"},
                "Lake Victoria FM": {"region": "Western", "reach": 700000, "cost_per_spot": 35000, "primary_audience": ["General"], "best_for": ["Community News"], "price_tier": "Economy"}
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
    
    def get_all_stations_with_contacts(self):
        """Get all stations with contact details"""
        stations_with_contacts = []
        for media_type, stations in self.stations.items():
            for name, info in stations.items():
                contacts = get_station_contacts(name)
                stations_with_contacts.append({
                    "name": name,
                    "media_type": media_type,
                    "region": info["region"],
                    "reach": info["reach"],
                    "price_tier": info["price_tier"],
                    "contacts": contacts
                })
        return stations_with_contacts

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
            with st.spinner("Logging in..."):
                time.sleep(0.5)
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
    admin_tab1, admin_tab2, admin_tab3, admin_tab4, admin_tab5 = st.tabs([
        "📊 Performance", "📋 Pending Approvals", "👥 All Leads", "📺 Media Directory", "🏢 Companies"
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
                    st.markdown(f'<div class="metric-card"><div class="metric-label">🔥 Hot Leads</div><div class="metric-value">{lead_stats["hot"]}</div></div>', unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">✅ Converted</div><div class="metric-value">{lead_stats["converted"]}</div></div>', unsafe_allow_html=True)
                with col4:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">📋 Bookings</div><div class="metric-value">{booking_stats["total"]}</div></div>', unsafe_allow_html=True)
                
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
                        with st.spinner("Processing approval..."):
                            update_booking_status(booking['booking_id'], 'approved', admin_notes if admin_notes else None)
                            st.success(f"Booking #{booking['booking_id']} approved! Email notification sent to client.")
                            time.sleep(1)
                            st.rerun()
                    
                    if st.button(f"❌ Reject / Suspend", key=f"suspend_{booking['booking_id']}"):
                        with st.spinner("Processing..."):
                            update_booking_status(booking['booking_id'], 'suspended', admin_notes if admin_notes else None)
                            st.warning(f"Booking #{booking['booking_id']} suspended.")
                            time.sleep(1)
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
    # ADMIN TAB 3: All Leads with Scoring
    # ========================================================================
    with admin_tab3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 👥 All Audience Leads (With Lead Scoring)")
        
        if not all_leads.empty:
            # Lead scoring summary
            lead_stats = get_lead_statistics()
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">🔥 Hot Leads</div><div class="metric-value">{lead_stats["hot"]}</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">🟡 Warm Leads</div><div class="metric-value">{lead_stats["warm"]}</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="metric-card"><div class="metric-label">❄️ Cold Leads</div><div class="metric-value">{lead_stats["cold"]}</div></div>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div class="metric-card"><div class="metric-label">✅ Conversion Rate</div><div class="metric-value">{lead_stats["conversion_rate"]}%</div></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            status_filter = st.selectbox("Filter by Status", ["All", "New", "Contacted", "Converted", "Hot", "Warm", "Cold"], key="admin_lead_filter")
            
            filtered_leads = all_leads
            if status_filter != "All":
                if status_filter in ["Hot", "Warm", "Cold"]:
                    filtered_leads = all_leads[all_leads['lead_score'] == status_filter.lower()]
                else:
                    filtered_leads = all_leads[all_leads['status'] == status_filter.lower()]
            
            for _, lead in filtered_leads.iterrows():
                if lead['lead_score'] == 'hot':
                    score_badge = '<span class="lead-hot">🔥 HOT LEAD</span>'
                elif lead['lead_score'] == 'warm':
                    score_badge = '<span class="lead-warm">🟡 WARM LEAD</span>'
                else:
                    score_badge = '<span class="lead-cold">❄️ COLD LEAD</span>'
                
                status_badge = '<span class="badge-new">NEW</span>' if lead['status'] == 'new' else '<span class="badge-pending">CONTACTED</span>' if lead['status'] == 'contacted' else '<span class="badge-confirmed">CONVERTED</span>'
                
                st.markdown(f"""
                <div class="lead-card">
                    <p><strong>{lead['lead_name']}</strong> {score_badge} {status_badge} - {lead['created_date'][:10] if lead['created_date'] else 'N/A'}</p>
                    <p><strong>Company:</strong> {lead['company_name']} | <strong>Phone:</strong> {lead['lead_phone']} | <strong>Email:</strong> {lead['lead_email']}</p>
                    <p><strong>Interested in:</strong> {lead['interest_product']}</p>
                    <p><strong>Message:</strong> {lead['message'][:200] if lead['message'] else 'No message'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if lead['status'] == 'new':
                        if st.button(f"📞 Mark Contacted", key=f"admin_contact_{lead['lead_id']}"):
                            update_lead_status(lead['lead_id'], 'contacted')
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
    # ADMIN TAB 4: Media Directory with Contacts
    # ========================================================================
    with admin_tab4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### 📺 📻 Media Directory with Contact Details")
        
        station_db = StationDatabase()
        all_stations = station_db.get_all_stations_with_contacts()
        
        # Filter by media type
        media_filter = st.selectbox("Filter by Media Type", ["All", "TV", "Radio"])
        
        filtered_stations = [s for s in all_stations if media_filter == "All" or s["media_type"] == media_filter]
        
        for station in filtered_stations:
            with st.expander(f"📺 {station['name']} ({station['media_type']}) - {station['region']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Reach:** {station['reach']:,}")
                    st.markdown(f"**Price Tier:** {station['price_tier']}")
                
                if station['contacts']:
                    with col2:
                        st.markdown("**Contact Information:**")
                        st.markdown(f"👤 **Contact Person:** {station['contacts']['contact_person']}")
                        st.markdown(f"📞 **Phone:** {station['contacts']['contact_phone']}")
                        st.markdown(f"📧 **Email:** {station['contacts']['contact_email']}")
                        st.markdown(f"📍 **Address:** {station['contacts']['address']}")
                        st.markdown(f"🌐 **Website:** {station['contacts']['website']}")
                else:
                    st.info("Contact details coming soon")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================================================
    # ADMIN TAB 5: Companies
    # ========================================================================
    with admin_tab5:
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
        cursor.execute("SELECT company_name, industry, email FROM companies WHERE company_id = ?", (company_id,))
        result = cursor.fetchone()
        company_name = result[0] if result else "Your Company"
        company_email = result[2] if result and result[2] else ""
        conn.close()
    except Exception as e:
        company_name = "Your Company"
        company_email = ""
    
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
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
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
            <div class="metric-label">🔥 Hot Leads</div>
            <div class="metric-value">{lead_stats['hot']}</div>
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
    
    with col6:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📈 Conv. Rate</div>
            <div class="metric-value">{lead_stats['conversion_rate']}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    df = get_company_data(company_id)
    logs_df = get_company_logs(company_id)
    bookings_df = get_booking_requests(company_id)
    leads_df = get_audience_leads(company_id)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Performance", "🎯 Smart Recommendations", "📺 TV/Radio Logs", "📋 My Bookings", "👥 Audience Leads", "📞 Station Contacts"
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
                                color='roas', color_continuous_scale='RdYlGn',
                                title="ROAS by Campaign")
                    fig.add_vline(x=2.0, line_dash="dash", line_color="#EF4444")
                    fig.update_layout(height=350, plot_bgcolor='white', showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Download button for chart
                    st.markdown(get_image_download_link(fig, "roas_by_campaign.png"), unsafe_allow_html=True)
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
            with st.spinner("Analyzing station data and generating recommendations..."):
                time.sleep(1)  # Simulate processing
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
                        contact_name = st.text_input("Your Name*", key="booking_name", value=company_name)
                        contact_email = st.text_input("Email Address*", key="booking_email", value=company_email)
                    with col2:
                        contact_phone = st
