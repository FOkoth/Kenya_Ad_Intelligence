"""
Station service - manages station data and contacts
"""
from database.db import get_station_contacts
from services.recommendations import StationDatabase as StationData

def get_all_stations():
    """Get all stations with contact details"""
    station_db = StationData()
    return station_db.get_all_stations_with_contacts()

def get_station_by_name(station_name):
    """Get a specific station by name"""
    station_db = StationData()
    for station in station_db.get_all_stations_with_contacts():
        if station['name'] == station_name:
            return station
    return None

def get_station_contact_details(station_name):
    """Get just the contact details for a station"""
    return get_station_contacts(station_name)
