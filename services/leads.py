"""
Lead management service
"""
from database.db import get_connection
from datetime import datetime
import pandas as pd

def add_lead(company_id, name, email, phone, product, message, source):
    """Add a new audience lead"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO audience_leads (company_id, lead_name, lead_email, lead_phone, interest_product, message, source, created_date, status)
        VALUES (?,?,?,?,?,?,?,?,?)''', (company_id, name, email, phone, product, message, source, datetime.now().isoformat(), 'new'))
    lead_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return lead_id

def get_leads(company_id=None, year=None, month=None):
    """Get leads with optional filters"""
    conn = get_connection()
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
    """Update lead status"""
    conn = get_connection()
    cursor = conn.cursor()
    converted_date = datetime.now().isoformat() if status == 'converted' else None
    cursor.execute("UPDATE audience_leads SET status=?, last_contacted=?, converted_date=? WHERE lead_id=?", 
                   (status, datetime.now().isoformat(), converted_date, lead_id))
    conn.commit()
    conn.close()
    return True

def get_lead_statistics(company_id=None, year=None, month=None):
    """Get lead statistics"""
    df = get_leads(company_id, year, month)
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
