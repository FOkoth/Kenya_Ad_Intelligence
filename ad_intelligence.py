"""
Ad Intelligence Kenya - Complete Platform
Professional Design with Time Filters & Better Layout
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
import calendar

# ============================================================================
# PAGE CONFIGURATION - MUST BE FIRST
# ============================================================================
st.set_page_config(
    page_title="Ad Intelligence Kenya",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================
def init_database():
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'client',
        company_id INTEGER,
        created_date TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS companies (
        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT UNIQUE NOT NULL,
        industry TEXT,
        email TEXT,
        phone TEXT,
        created_date TEXT,
        status TEXT DEFAULT 'active'
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS campaigns (
        campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        campaign_name TEXT,
        platform TEXT,
        spend_kes REAL,
        revenue_kes REAL,
        roas REAL,
        date TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS media_logs (
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
        booking_reference TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS booking_requests (
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
        notes TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS audience_leads (
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
        converted_date TEXT,
        last_contacted TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS stations (
        station_id INTEGER PRIMARY KEY AUTOINCREMENT,
        station_name TEXT UNIQUE,
        media_type TEXT,
        region TEXT,
        contact_person TEXT,
        contact_phone TEXT,
        contact_email TEXT,
        address TEXT,
        website TEXT
    )''')
    
    # Insert default stations
    cursor.execute("SELECT COUNT(*) FROM stations")
    if cursor.fetchone()[0] == 0:
        stations_data = [
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
        ]
        for s in stations_data:
            cursor.execute('INSERT OR IGNORE INTO stations (station_name, media_type, region, contact_person, contact_phone, contact_email, address, website) VALUES (?,?,?,?,?,?,?,?)', s)
    
    # Create default users
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role, company_id, created_date) VALUES (?,?,?,?,?)", 
                      ('admin', 'admin123', 'admin', None, datetime.now().isoformat()))
        companies = [('Safaricom', 'Telecommunications', 'advertising@safaricom.com', '+254700000000')]
        for c in companies:
            cursor.execute("INSERT INTO companies (company_name, industry, email, phone, created_date, status) VALUES (?,?,?,?,?,?)", 
                          (c[0], c[1], c[2], c[3], datetime.now().isoformat(), 'active'))
            company_id = cursor.lastrowid
            cursor.execute("INSERT INTO users (username, password, role, company_id, created_date) VALUES (?,?,?,?,?)", 
                          ('safaricom', 'client123', 'client', company_id, datetime.now().isoformat()))
            for day in range(90):
                date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
                spend = random.uniform(5000, 50000)
                revenue = spend * random.uniform(0.5, 4.0)
                cursor.execute("INSERT INTO campaigns (company_id, campaign_name, platform, spend_kes, revenue_kes, roas, date) VALUES (?,?,?,?,?,?,?)", 
                              (company_id, "Safaricom Campaign", random.choice(['Meta', 'Google']), spend, revenue, revenue/spend, date))
            
            # Sample bookings for testing
            sample_bookings = [
                ('pending_approval', (datetime.now() - timedelta(days=5)).isoformat()),
                ('approved', (datetime.now() - timedelta(days=10)).isoformat()),
                ('confirmed', (datetime.now() - timedelta(days=15)).isoformat()),
            ]
            for status, date in sample_bookings:
                cursor.execute('''INSERT INTO booking_requests 
                    (company_id, station_name, selected_stations, media_type, preferred_time, budget_kes, duration_days, target_audience, campaign_goal, contact_name, contact_email, contact_phone, status, request_date)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (company_id, 'Citizen TV', 'Citizen TV, Radio Jambo', 'Mixed', '2024-01-15', 500000, 14, 'Mass Market', 'Brand Awareness', 'John Doe', 'john@example.com', '+254712345678', status, date))
    
    conn.commit()
    conn.close()

init_database()

# ============================================================================
# DATABASE HELPER FUNCTIONS
# ============================================================================
def get_station_contacts(station_name):
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute("SELECT contact_person, contact_phone, contact_email, address, website FROM stations WHERE station_name = ?", (station_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {'contact_person': result[0], 'contact_phone': result[1], 'contact_email': result[2], 'address': result[3], 'website': result[4]}
    return None

def get_company_data(company_id, year=None, month=None):
    conn = sqlite3.connect('ad_intelligence.db')
    query = "SELECT * FROM campaigns WHERE company_id = ?"
    params = [company_id]
    if year:
        query += " AND strftime('%Y', date) = ?"
        params.append(str(year))
    if month:
        query += " AND strftime('%m', date) = ?"
        params.append(f"{month:02d}")
    query += " ORDER BY date DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_all_companies():
    conn = sqlite3.connect('ad_intelligence.db')
    df = pd.read_sql_query("SELECT company_id, company_name, industry, email, phone FROM companies WHERE status = 'active'", conn)
    conn.close()
    return df

def create_booking_request(company_id, stations_list, campaign_goal, budget, duration, audience, region, contact_name, contact_email, contact_phone, notes=""):
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    stations_str = ", ".join(stations_list)
    cursor.execute('''INSERT INTO booking_requests 
        (company_id, station_name, selected_stations, media_type, preferred_time, budget_kes, duration_days, target_audience, campaign_goal, contact_name, contact_email, contact_phone, status, request_date, status_updated_date, notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (company_id, stations_list[0] if stations_list else "Multiple", stations_str, "Mixed", datetime.now().strftime("%Y-%m-%d"),
         budget, duration, audience, campaign_goal, contact_name, contact_email, contact_phone, 'pending_approval', datetime.now().isoformat(), datetime.now().isoformat(), notes))
    booking_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return booking_id

def get_booking_requests(company_id=None, year=None, month=None):
    conn = sqlite3.connect('ad_intelligence.db')
    if company_id:
        query = "SELECT * FROM booking_requests WHERE company_id = ?"
        params = [company_id]
        if year:
            query += " AND strftime('%Y', request_date) = ?"
            params.append(str(year))
        if month:
            query += " AND strftime('%m', request_date) = ?"
            params.append(f"{month:02d}")
        query += " ORDER BY request_date DESC"
        df = pd.read_sql_query(query, conn, params=params)
    else:
        query = "SELECT br.*, c.company_name FROM booking_requests br JOIN companies c ON br.company_id = c.company_id"
        params = []
        if year:
            query += " WHERE strftime('%Y', br.request_date) = ?"
            params.append(str(year))
        if month and year:
            query += " AND strftime('%m', br.request_date) = ?"
            params.append(f"{month:02d}")
        query += " ORDER BY br.request_date DESC"
        df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def update_booking_status(booking_id, status, admin_notes=None):
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    if status == 'approved':
        cursor.execute("UPDATE booking_requests SET status=?, status_updated_date=?, approved_date=?, admin_notes=? WHERE booking_id=?", (status, now, now, admin_notes, booking_id))
    elif status == 'confirmed':
        cursor.execute("UPDATE booking_requests SET status=?, status_updated_date=?, confirmed_date=? WHERE booking_id=?", (status, now, now, booking_id))
    else:
        cursor.execute("UPDATE booking_requests SET status=?, status_updated_date=?, admin_notes=? WHERE booking_id=?", (status, now, admin_notes, booking_id))
    conn.commit()
    conn.close()
    return True

def get_booking_statistics(company_id=None, year=None, month=None):
    df = get_booking_requests(company_id, year, month)
    if df.empty:
        return {'total': 0, 'pending_approval': 0, 'approved': 0, 'confirmed': 0, 'suspended': 0}
    return {
        'total': len(df),
        'pending_approval': len(df[df['status'] == 'pending_approval']),
        'approved': len(df[df['status'] == 'approved']),
        'confirmed': len(df[df['status'] == 'confirmed']),
        'suspended': len(df[df['status'] == 'suspended'])
    }

def add_audience_lead(company_id, name, email, phone, product, message, source):
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO audience_leads (company_id, lead_name, lead_email, lead_phone, interest_product, message, source, created_date, status)
        VALUES (?,?,?,?,?,?,?,?,?)''', (company_id, name, email, phone, product, message, source, datetime.now().isoformat(), 'new'))
    lead_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return lead_id

def get_audience_leads(company_id=None, year=None, month=None):
    conn = sqlite3.connect('ad_intelligence.db')
    if company_id:
        query = "SELECT * FROM audience_leads WHERE company_id = ?"
        params = [company_id]
        if year:
            query += " AND strftime('%Y', created_date) = ?"
            params.append(str(year))
        if month:
            query += " AND strftime('%m', created_date) = ?"
            params.append(f"{month:02d}")
        query += " ORDER BY created_date DESC"
        df = pd.read_sql_query(query, conn, params=params)
    else:
        query = "SELECT al.*, c.company_name FROM audience_leads al JOIN companies c ON al.company_id = c.company_id"
        params = []
        if year:
            query += " WHERE strftime('%Y', al.created_date) = ?"
            params.append(str(year))
        if month and year:
            query += " AND strftime('%m', al.created_date) = ?"
            params.append(f"{month:02d}")
        query += " ORDER BY al.created_date DESC"
        df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def update_lead_status(lead_id, status):
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    converted_date = datetime.now().isoformat() if status == 'converted' else None
    cursor.execute("UPDATE audience_leads SET status=?, last_contacted=?, converted_date=? WHERE lead_id=?", (status, datetime.now().isoformat(), converted_date, lead_id))
    conn.commit()
    conn.close()
    return True

def get_lead_statistics(company_id=None, year=None, month=None):
    df = get_audience_leads(company_id, year, month)
    if df.empty:
        return {'total': 0, 'new': 0, 'contacted': 0, 'converted': 0, 'conversion_rate': 0}
    total = len(df)
    converted = len(df[df['status'] == 'converted'])
    return {
        'total': total,
        'new': len(df[df['status'] == 'new']),
        'contacted': len(df[df['status'] == 'contacted']),
        'converted': converted,
        'conversion_rate': round(converted/total*100, 1) if total > 0 else 0
    }

def get_available_years(company_id=None):
    conn = sqlite3.connect('ad_intelligence.db')
    if company_id:
        df = pd.read_sql_query("SELECT DISTINCT strftime('%Y', date) as year FROM campaigns WHERE company_id = ? UNION SELECT DISTINCT strftime('%Y', request_date) FROM booking_requests WHERE company_id = ?", conn, params=(company_id, company_id))
    else:
        df = pd.read_sql_query("SELECT DISTINCT strftime('%Y', date) as year FROM campaigns UNION SELECT DISTINCT strftime('%Y', request_date) FROM booking_requests", conn)
    conn.close()
    years = df['year'].dropna().tolist()
    return sorted(years, reverse=True) if years else [datetime.now().year]

# ============================================================================
# STATION DATABASE CLASS
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
    
    def get_all_stations_with_contacts(self):
        result = []
        for media_type, stations in self.stations.items():
            for name, info in stations.items():
                contacts = get_station_contacts(name)
                result.append({"name": name, "media_type": media_type, "region": info["region"], "reach": info["reach"], "price_tier": info["price_tier"], "contacts": contacts})
        return result

class MediaRecommendationEngine:
    def __init__(self):
        self.station_db = StationDatabase()
    
    def recommend_stations(self, campaign_goal, budget, duration_days, target_audience, region_type, selected_area=None):
        available = self.station_db.get_stations_by_region(region_type)
        recommendations = []
        for media_type, stations in available.items():
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
                        "price_tier": station["price_tier"],
                        "score": score
                    })
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:5]

# ============================================================================
# CUSTOM CSS - PROFESSIONAL DESIGN
# ============================================================================
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Header styling - VISIBLE AND BEAUTIFUL */
    .app-header {
        background: linear-gradient(135deg, #004953 0%, #006B7A 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        box-shadow: 0 4px 20px rgba(0,73,83,0.15);
    }
    .header-title h1 {
        color: white;
        margin: 0;
        font-size: 1.6rem;
        font-weight: 600;
    }
    .header-title p {
        color: rgba(255,255,255,0.85);
        margin: 0.25rem 0 0 0;
        font-size: 0.85rem;
    }
    .logout-btn {
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 10px;
        padding: 0.5rem 1.2rem;
        color: white;
        cursor: pointer;
        transition: all 0.2s;
        font-weight: 500;
    }
    .logout-btn:hover {
        background: rgba(255,255,255,0.25);
        transform: translateY(-1px);
    }
    
    /* Login page styling */
    .login-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        border: 1px solid #E2E8F0;
    }
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-header h2 {
        color: #004953;
        margin-bottom: 0.5rem;
    }
    .login-header p {
        color: #64748B;
        font-size: 0.85rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border-left: 4px solid #C6A43F;
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #004953;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    /* Section cards */
    .section-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1E293B;
        margin-bottom: 1.2rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #C6A43F;
        display: inline-block;
    }
    
    /* Recommendation cards */
    .rec-card {
        background: linear-gradient(135deg, #004953 0%, #003540 100%);
        border-radius: 16px;
        padding: 1.2rem;
        color: white;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .rec-card:hover {
        transform: translateX(5px);
    }
    .rec-card h4 {
        color: #C6A43F;
        margin: 0 0 0.6rem 0;
        font-size: 1.1rem;
    }
    .rec-card p {
        margin: 0.3rem 0;
        font-size: 0.85rem;
        opacity: 0.9;
    }
    
    /* Booking cards - improved layout */
    .booking-card {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: all 0.2s;
    }
    .booking-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .booking-card-pending {
        border-left: 5px solid #F59E0B;
        background: #FFFBEB;
    }
    .booking-card-approved {
        border-left: 5px solid #8B5CF6;
        background: #F5F3FF;
    }
    .booking-card-confirmed {
        border-left: 5px solid #10B981;
        background: #ECFDF5;
    }
    .booking-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 0.75rem;
    }
    .booking-id {
        font-weight: 700;
        font-size: 1rem;
        color: #1E293B;
    }
    .booking-date {
        font-size: 0.75rem;
        color: #64748B;
    }
    .booking-details {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 0.5rem;
        margin: 0.75rem 0;
    }
    .booking-detail-item {
        font-size: 0.85rem;
    }
    .booking-detail-label {
        font-weight: 600;
        color: #475569;
    }
    
    /* Lead cards */
    .lead-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: all 0.2s;
    }
    .lead-card:hover {
        border-color: #C6A43F;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .lead-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 0.75rem;
    }
    .lead-name {
        font-weight: 700;
        font-size: 1rem;
        color: #1E293B;
    }
    .lead-contact {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 0.5rem;
        margin: 0.5rem 0;
        font-size: 0.8rem;
        color: #475569;
    }
    .lead-message {
        background: white;
        padding: 0.75rem;
        border-radius: 12px;
        margin-top: 0.5rem;
        font-size: 0.85rem;
        color: #334155;
        border-left: 3px solid #C6A43F;
    }
    
    /* Status badges */
    .badge-pending { background: #F59E0B; color: white; padding: 0.25rem 0.9rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
    .badge-approved { background: #8B5CF6; color: white; padding: 0.25rem 0.9rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
    .badge-confirmed { background: #10B981; color: white; padding: 0.25rem 0.9rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
    .badge-new { background: #10B981; color: white; padding: 0.25rem 0.9rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
    .badge-contacted { background: #F59E0B; color: white; padding: 0.25rem 0.9rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
    .badge-converted { background: #8B5CF6; color: white; padding: 0.25rem 0.9rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; display: inline-block; }
    
    /* Time filter bar */
    .time-filter-bar {
        background: #F8FAFC;
        padding: 1rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        display: flex;
        gap: 1rem;
        align-items: center;
        flex-wrap: wrap;
    }
    
    /* Button styling */
    .stButton > button {
        background: #004953;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s;
        width: 100%;
    }
    .stButton > button:hover {
        background: #006B7A;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,73,83,0.2);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        background: #F8FAFC;
        border-radius: 16px;
        font-size: 0.75rem;
        color: #64748B;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #F1F5F9;
        padding: 0.5rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #004953;
        color: white;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #F8FAFC;
        border-radius: 10px;
        font-weight: 500;
    }
    
    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# TIME FILTER COMPONENT
# ============================================================================
def render_time_filter(company_id=None):
    """Render year and month selectors for filtering historical data"""
    available_years = get_available_years(company_id)
    current_year = datetime.now().year
    
    col1, col2 = st.columns([1, 1])
    with col1:
        selected_year = st.selectbox(
            "📅 Select Year",
            options=available_years,
            index=0 if available_years else 0,
            key="year_filter"
        )
    with col2:
        months = ["All Months", "January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", "December"]
        selected_month_name = st.selectbox("📆 Select Month", options=months, key="month_filter")
        selected_month = None if selected_month_name == "All Months" else months.index(selected_month_name)
    
    return selected_year, selected_month

# ============================================================================
# LOGIN SYSTEM
# ============================================================================
def check_login(username, password):
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, role, company_id FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result

def show_login():
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
        
        username = st.text_input("Username", placeholder="Enter your username", key="login_username")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
        
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
                st.error("❌ Invalid username or password")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #E2E8F0;">
            <p style="font-size: 0.75rem; color: #64748B;">Demo Accounts:</p>
            <p style="font-size: 0.7rem; color: #475569;">📊 Admin: <strong>admin</strong> / <strong>admin123</strong></p>
            <p style="font-size: 0.7rem; color: #475569;">🏢 Client: <strong>safaricom</strong> / <strong>client123</strong></p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# ADMIN DASHBOARD
# ============================================================================
def show_admin_dashboard():
    # Header with logout
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown("""
        <div class="header-title">
            <h1>📊 Admin Dashboard</h1>
            <p>Complete overview of all advertising activities</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    
    # Time filter
    st.markdown('<div class="time-filter-bar">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        selected_year = st.selectbox("📅 Select Year", options=[2023, 2024, 2025], index=1)
    with col2:
        months = ["All Months", "January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", "December"]
        selected_month_name = st.selectbox("📆 Select Month", options=months)
        selected_month = None if selected_month_name == "All Months" else months.index(selected_month_name)
    st.markdown('</div>', unsafe_allow_html=True)
    
    all_companies = get_all_companies()
    all_bookings = get_booking_requests(year=selected_year, month=selected_month)
    all_leads = get_audience_leads(year=selected_year, month=selected_month)
    
    # Statistics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">🏢 Companies</div><div class="metric-value">{len(all_companies)}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">📋 Bookings</div><div class="metric-value">{len(all_bookings)}</div></div>', unsafe_allow_html=True)
    with col3:
        pending = len(all_bookings[all_bookings['status'] == 'pending_approval']) if not all_bookings.empty else 0
        st.markdown(f'<div class="metric-card"><div class="metric-label">⏳ Pending</div><div class="metric-value">{pending}</div></div>', unsafe_allow_html=True)
    with col4:
        confirmed = len(all_bookings[all_bookings['status'] == 'confirmed']) if not all_bookings.empty else 0
        st.markdown(f'<div class="metric-card"><div class="metric-label">✅ Confirmed</div><div class="metric-value">{confirmed}</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card"><div class="metric-label">👥 Leads</div><div class="metric-value">{len(all_leads)}</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Pending Approvals", "👥 All Leads", "📺 Media Directory", "🏢 Companies"])
    
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
                        <span class="booking-date">{b['request_date'][:10] if b['request_date'] else 'N/A'}</span>
                    </div>
                    <div class="booking-details">
                        <div class="booking-detail-item"><span class="booking-detail-label">Company:</span> {b.get('company_name', 'N/A')}</div>
                        <div class="booking-detail-item"><span class="booking-detail-label">Stations:</span> {b.get('selected_stations', b['station_name'])}</div>
                        <div class="booking-detail-item"><span class="booking-detail-label">Budget:</span> KES {b['budget_kes']:,.0f}</div>
                        <div class="booking-detail-item"><span class="booking-detail-label">Duration:</span> {b['duration_days']} days</div>
                        <div class="booking-detail-item"><span class="booking-detail-label">Contact:</span> {b['contact_name']}</div>
                        <div class="booking-detail-item"><span class="booking-detail-label">Email:</span> {b['contact_email']}</div>
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
    
    with tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">All Audience Leads</p>', unsafe_allow_html=True)
        if not all_leads.empty:
            lead_stats = get_lead_statistics(year=selected_year, month=selected_month)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">📊 Total</div><div class="metric-value">{lead_stats["total"]}</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">🆕 New</div><div class="metric-value">{lead_stats["new"]}</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="metric-card"><div class="metric-label">✅ Converted</div><div class="metric-value">{lead_stats["converted"]}</div></div>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div class="metric-card"><div class="metric-label">📈 Conv. Rate</div><div class="metric-value">{lead_stats["conversion_rate"]}%</div></div>', unsafe_allow_html=True)
            st.markdown("---")
            for _, lead in all_leads.iterrows():
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
                        <span>🏢 {lead.get('company_name', 'N/A')}</span>
                    </div>
                    <div class="lead-message">
                        <strong>💬 Interest:</strong> {lead['interest_product']}<br>
                        <strong>📝 Message:</strong> {lead['message'][:150] if lead['message'] else 'No message'}
                    </div>
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
    
    with tab3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Media Directory with Contacts</p>', unsafe_allow_html=True)
        station_db = StationDatabase()
        for station in station_db.get_all_stations_with_contacts():
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
    
    with tab4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Registered Companies</p>', unsafe_allow_html=True)
        if not all_companies.empty:
            st.dataframe(all_companies, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# CLIENT PORTAL
# ============================================================================
def show_client_portal():
    company_id = st.session_state.company_id
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    cursor.execute("SELECT company_name, email FROM companies WHERE company_id=?", (company_id,))
    result = cursor.fetchone()
    company_name = result[0] if result else "Your Company"
    company_email = result[1] if result else ""
    conn.close()
    
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
    st.markdown('<div class="time-filter-bar">', unsafe_allow_html=True)
    available_years = get_available_years(company_id)
    col1, col2 = st.columns([1, 1])
    with col1:
        selected_year = st.selectbox("📅 Select Year", options=available_years, index=0 if available_years else 0)
    with col2:
        months = ["All Months", "January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", "December"]
        selected_month_name = st.selectbox("📆 Select Month", options=months)
        selected_month = None if selected_month_name == "All Months" else months.index(selected_month_name)
    st.markdown('</div>', unsafe_allow_html=True)
    
    lead_stats = get_lead_statistics(company_id, selected_year, selected_month)
    booking_stats = get_booking_statistics(company_id, selected_year, selected_month)
    
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
        
        if 'recs' not in st.session_state:
            st.session_state.recs = None
        if 'rec_params' not in st.session_state:
            st.session_state.rec_params = {}
        
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
        
        if st.session_state.recs:
            st.markdown("---")
            st.markdown("### 🏆 Recommended Stations")
            for i, r in enumerate(st.session_state.recs[:3]):
                price_icon = "🟢" if r['price_tier'] == "Economy" else "🟡" if r['price_tier'] == "Standard" else "🔴"
                st.markdown(f"""
                <div class="rec-card">
                    <h4>#{i+1} {r['station_name']} ({r['media_type']}) {price_icon} {r['price_tier']}</h4>
                    <p>📊 Reach: {r['reach']:,} | 💰 Cost per spot: KES {r['cost_per_spot']:,}</p>
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
                            bid = create_booking_request(company_id, selected, campaign_goal, budget, duration, target_audience, region_type, name, email, phone, notes)
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
        bookings = get_booking_requests(company_id, selected_year, selected_month)
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
                        <span class="booking-date">{b['request_date'][:10] if b['request_date'] else 'N/A'}</span>
                    </div>
                    <div class="booking-details">
                        <div class="booking-detail-item"><span class="booking-detail-label">Stations:</span> {b.get('selected_stations', b['station_name'])}</div>
                        <div class="booking-detail-item"><span class="booking-detail-label">Budget:</span> KES {b['budget_kes']:,.0f}</div>
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
            test_name = st.text_input("Name", "John Kamau", key="test_name")
            test_email = st.text_input("Email", "john@example.com", key="test_email")
            test_phone = st.text_input("Phone", "+254712345678", key="test_phone")
            test_product = st.text_input("Product Interest", "Your Service", key="test_product")
            test_msg = st.text_area("Message", "I'm very interested! Please call me.", key="test_msg")
            if st.button("Submit Test Lead", key="submit_test"):
                add_audience_lead(company_id, test_name, test_email, test_phone, test_product, test_msg, "Website")
                st.success("Test lead added!")
                st.rerun()
        
        leads = get_audience_leads(company_id, selected_year, selected_month)
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
        station_db = StationDatabase()
        region_filter = st.selectbox("Filter by Region", ["All", "National", "Coast", "Western", "Central"])
        
        for station in station_db.get_all_stations_with_contacts():
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
    
    # Tab 5: Performance with time filter
    with tab5:
        df = get_company_data(company_id, selected_year, selected_month)
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
                st.markdown(f'<div class="metric-card"><div class="metric-label">📈 ROAS</div><div class="metric-value" style="color:{roas_color};">{avg_roas:.2f}x</div></div>', unsafe_allow_html=True)
            
            campaign_roas = df.groupby('campaign_name')['roas'].mean().reset_index()
            fig = px.bar(campaign_roas, x='roas', y='campaign_name', orientation='h', color='roas', color_continuous_scale='RdYlGn')
            fig.add_vline(x=2.0, line_dash="dash", line_color="#EF4444", annotation_text="Target (2x)")
            fig.update_layout(height=400, plot_bgcolor='white', showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No campaign data available for selected period")

# ============================================================================
# MAIN
# ============================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.recs = None
    st.session_state.rec_params = {}

if st.session_state.logged_in:
    if st.session_state.role == 'admin':
        show_admin_dashboard()
    else:
        show_client_portal()
else:
    show_login()

st.markdown('<div class="footer"><p>© 2024 Ad Intelligence Kenya | AI-Powered Media Recommendations & Lead Management</p></div>', unsafe_allow_html=True)
