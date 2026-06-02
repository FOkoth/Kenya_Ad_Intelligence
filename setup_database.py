"""
Database Setup for Ad Intelligence Platform
Run this file ONCE to create all tables
"""
import sqlite3
from datetime import datetime

def create_database():
    """Create all tables needed for the platform"""
    
    conn = sqlite3.connect('ad_intelligence.db')
    cursor = conn.cursor()
    
    # Table 1: Users (for login)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'client',  -- 'admin' or 'client'
        company_id INTEGER,
        created_date TEXT
    )
    ''')
    
    # Table 2: Companies/Clients
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
    
    # Table 3: Campaigns per company
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS campaigns (
        campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        campaign_name TEXT,
        platform TEXT,
        start_date TEXT,
        end_date TEXT,
        spend_kes REAL,
        revenue_kes REAL,
        roas REAL,
        date TEXT,
        FOREIGN KEY (company_id) REFERENCES companies (company_id)
    )
    ''')
    
    # Table 4: Media Logs (TV/Radio airtime records)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS media_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        campaign_id INTEGER,
        station_name TEXT,
        media_type TEXT,  -- 'TV' or 'Radio'
        spot_time TEXT,
        duration_seconds INTEGER,
        cost_kes REAL,
        estimated_reach INTEGER,
        log_date TEXT,
        FOREIGN KEY (company_id) REFERENCES companies (company_id)
    )
    ''')
    
    # Table 5: Products per company
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
    
    conn.commit()
    print("✅ Database tables created successfully!")
    
    # Insert default users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
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
        ]
        
        for company in companies:
            cursor.execute('''
            INSERT INTO companies (company_name, industry, email, phone, created_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (company[0], company[1], company[2], company[3], datetime.now().isoformat(), 'active'))
            
            # Get the company_id
            company_id = cursor.lastrowid
            
            # Create client user for this company
            username = company[0].lower().replace(' ', '')
            cursor.execute('''
            INSERT INTO users (username, password, role, company_id, created_date)
            VALUES (?, ?, ?, ?, ?)
            ''', (username, 'client123', 'client', company_id, datetime.now().isoformat()))
        
        conn.commit()
        print("✅ Default users created:")
        print("   Admin: username='admin', password='admin123'")
        print("   Safaricom: username='safaricom', password='client123'")
        print("   KCB Bank: username='kcb bank', password='client123'")
        print("   Tourism Kenya: username='tourismkenya', password='client123'")
    
    conn.close()
    return True

def generate_sample_campaign_data():
    """Generate sample campaign data for testing"""
    
    import random
    import numpy as np
    
    conn = sqlite3.connect('ad_intelligence.db')
    
    # Get all companies
    companies_df = pd.read_sql_query("SELECT company_id, company_name FROM companies", conn)
    
    for _, company in companies_df.iterrows():
        company_id = company['company_id']
        
        # Generate 30 days of sample data
        for day in range(30):
            date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
            
            spend = random.uniform(5000, 50000)
            revenue = spend * random.uniform(0.5, 4.0)
            roas = revenue / spend
            
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO campaigns (company_id, campaign_name, platform, start_date, end_date, spend_kes, revenue_kes, roas, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (company_id, f"{company['company_name']} Campaign", 
                  random.choice(['Meta', 'Google', 'TikTok']),
                  date, date, spend, revenue, roas, date))
    
    conn.commit()
    conn.close()
    print("✅ Sample campaign data generated!")

# Run the setup
if __name__ == "__main__":
    import pandas as pd
    from datetime import timedelta
    
    create_database()
    generate_sample_campaign_data()
    print("\n🎯 Database setup complete! You can now run your Streamlit app.")