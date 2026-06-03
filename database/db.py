"""
Database module - Handles all database operations
"""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

DB_PATH = 'ad_intelligence.db'

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def init_database():
    """Initialize database with all tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'client',
        company_id INTEGER,
        created_date TEXT
    )''')
    
    # Companies table
    cursor.execute('''CREATE TABLE IF NOT EXISTS companies (
        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT UNIQUE NOT NULL,
        industry TEXT,
        email TEXT,
        phone TEXT,
        created_date TEXT,
        status TEXT DEFAULT 'active'
    )''')
    
    # Campaigns table
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
    
    # Media logs table
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
    
    # Booking requests table
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
    
    # Audience leads table
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
    
    # Stations table
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
            
            # Sample bookings
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

def get_station_contacts(station_name):
    """Get contact details for a station"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT contact_person, contact_phone, contact_email, address, website FROM stations WHERE station_name = ?", (station_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {'contact_person': result[0], 'contact_phone': result[1], 'contact_email': result[2], 'address': result[3], 'website': result[4]}
    return None

def get_company_data(company_id, year=None, month=None):
    """Get campaign data for a company with optional year/month filter"""
    conn = get_connection()
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
    """Get all active companies"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT company_id, company_name, industry, email, phone FROM companies WHERE status = 'active'", conn)
    conn.close()
    return df

def get_company_by_id(company_id):
    """Get company details by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT company_name, email, phone FROM companies WHERE company_id = ?", (company_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {'name': result[0], 'email': result[1], 'phone': result[2]}
    return None

def get_available_years(company_id=None):
    """Get available years for filtering"""
    conn = get_connection()
    if company_id:
        df = pd.read_sql_query("SELECT DISTINCT strftime('%Y', date) as year FROM campaigns WHERE company_id = ? UNION SELECT DISTINCT strftime('%Y', request_date) FROM booking_requests WHERE company_id = ?", conn, params=(company_id, company_id))
    else:
        df = pd.read_sql_query("SELECT DISTINCT strftime('%Y', date) as year FROM campaigns UNION SELECT DISTINCT strftime('%Y', request_date) FROM booking_requests", conn)
    conn.close()
    years = df['year'].dropna().tolist()
    return sorted(years, reverse=True) if years else [datetime.now().year]
