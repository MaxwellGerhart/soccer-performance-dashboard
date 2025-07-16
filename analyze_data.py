import sqlite3
import json
import numpy as np
from collections import defaultdict

def analyze_statsbomb_data():
    """Analyze the StatsBomb data structure to understand what's available for trait calculation"""
    
    conn = sqlite3.connect('data/soccer.db')
    cursor = conn.cursor()
    
    print("=== STATSBOMB DATA ANALYSIS FOR TRAIT CALCULATION ===\n")
    
    # Check available columns
    cursor.execute("PRAGMA table_info(events)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Key columns for our traits
    relevant_columns = [
        'location', 'pass_end_location', 'under_pressure', 'timestamp', 
        'duration', 'pass_outcome_name', 'pass_length', 'pass_angle',
        'ball_receipt_outcome_name', 'miscontrol_aerial_won', 'carry_end_location',
        'pass_recipient_name', 'pass_height_name', 'pass_type_name'
    ]
    
    available_relevant = [col for col in relevant_columns if col in columns]
    print(f"Available relevant columns: {available_relevant}")
    
    # Check for location data
    cursor.execute("SELECT COUNT(*) FROM events WHERE location IS NOT NULL")
    location_count = cursor.fetchone()[0]
    print(f"Events with location data: {location_count}")
    
    # Check for pass data
    cursor.execute("SELECT COUNT(*) FROM events WHERE type_name = 'Pass' AND pass_end_location IS NOT NULL")
    pass_location_count = cursor.fetchone()[0]
    print(f"Pass events with end location: {pass_location_count}")
    
    # Check for under pressure data
    cursor.execute("SELECT COUNT(*) FROM events WHERE under_pressure = 1")
    pressure_count = cursor.fetchone()[0]
    print(f"Events under pressure: {pressure_count}")
    
    # Check for timestamp/duration data
    cursor.execute("SELECT COUNT(*) FROM events WHERE timestamp IS NOT NULL AND duration IS NOT NULL")
    timing_count = cursor.fetchone()[0]
    print(f"Events with timing data: {timing_count}")
    
    # Sample some location data to understand format
    cursor.execute("SELECT location, pass_end_location FROM events WHERE location IS NOT NULL LIMIT 5")
    location_samples = cursor.fetchall()
    print(f"\nSample location data:")
    for i, (loc, end_loc) in enumerate(location_samples):
        print(f"  {i+1}. Start: {loc}, End: {end_loc}")
    
    conn.close()
    
    return available_relevant

if __name__ == "__main__":
    analyze_statsbomb_data()
