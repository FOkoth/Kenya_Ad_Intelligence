"""
Booking management service
"""
from database.db import get_connection
from datetime import datetime
import pandas as pd

def create_booking(company_id, stations_list, campaign_goal, budget, duration, audience, region, contact_name, contact_email, contact_phone, notes=""):
    """Create a new booking request"""
    conn = get_connection()
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

def get_bookings(company_id=None, year=None, month=None):
    """Get bookings with optional filters"""
    conn = get_connection()
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
    """Update booking status"""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    if status == 'approved':
        cursor.execute("UPDATE booking_requests SET status=?, status_updated_date=?, approved_date=?, admin_notes=? WHERE booking_id=?", 
                      (status, now, now, admin_notes, booking_id))
    elif status == 'confirmed':
        cursor.execute("UPDATE booking_requests SET status=?, status_updated_date=?, confirmed_date=? WHERE booking_id=?", 
                      (status, now, now, booking_id))
    else:
        cursor.execute("UPDATE booking_requests SET status=?, status_updated_date=?, admin_notes=? WHERE booking_id=?", 
                      (status, now, admin_notes, booking_id))
    conn.commit()
    conn.close()
    return True

def get_booking_statistics(company_id=None, year=None, month=None):
    """Get booking statistics"""
    df = get_bookings(company_id, year, month)
    if df.empty:
        return {'total': 0, 'pending_approval': 0, 'approved': 0, 'confirmed': 0, 'suspended': 0}
    return {
        'total': len(df),
        'pending_approval': len(df[df['status'] == 'pending_approval']),
        'approved': len(df[df['status'] == 'approved']),
        'confirmed': len(df[df['status'] == 'confirmed']),
        'suspended': len(df[df['status'] == 'suspended'])
    }
