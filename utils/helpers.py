"""
Helper utility functions
"""
from datetime import datetime

def format_currency(amount):
    """Format number as Kenyan Shillings"""
    return f"KES {amount:,.0f}"

def format_date(date_string):
    """Format date string to readable format"""
    if not date_string:
        return "N/A"
    return date_string[:10]

def get_month_name(month_number):
    """Get month name from number"""
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    if month_number and 1 <= month_number <= 12:
        return months[month_number - 1]
    return "All Months"

def get_available_months():
    """Get list of months for dropdown"""
    return ["All Months", "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"]
