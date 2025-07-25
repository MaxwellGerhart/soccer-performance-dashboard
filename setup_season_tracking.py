import sqlite3
import os

def add_season_tracking_schema():
    """Add season and date tracking to the existing database without affecting current data"""
    
    conn = sqlite3.connect('data/ncaa_soccer.db')
    cursor = conn.cursor()
    
    print("Adding season tracking schema...")
    
    # Add season and data_date columns to existing tables
    try:
        cursor.execute("ALTER TABLE players ADD COLUMN season TEXT DEFAULT '2024'")
        print("✅ Added season column to players table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  Season column already exists in players table")
        else:
            raise e
    
    try:
        cursor.execute("ALTER TABLE players ADD COLUMN data_date TEXT DEFAULT '2024-12-31'")
        print("✅ Added data_date column to players table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  Data_date column already exists in players table")
        else:
            raise e
    
    # Update existing 2024 data with proper labels
    cursor.execute("UPDATE players SET season = '2024' WHERE season IS NULL")
    cursor.execute("UPDATE players SET data_date = '2024-12-31' WHERE data_date IS NULL")
    print("✅ Updated existing players with 2024 season labels")
    
    # Create data snapshots tracking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season TEXT NOT NULL,
            snapshot_date TEXT NOT NULL,
            description TEXT,
            file_path TEXT,
            total_players INTEGER,
            total_games INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_current BOOLEAN DEFAULT FALSE,
            UNIQUE(season, snapshot_date)
        )
    """)
    print("✅ Created data_snapshots table")
    
    # Add the current 2024 data as a snapshot
    cursor.execute("""
        INSERT OR REPLACE INTO data_snapshots 
        (season, snapshot_date, description, total_players, is_current)
        VALUES (?, ?, ?, ?, ?)
    """, ('2024', '2024-12-31', 'Final 2024 season data', 
          cursor.execute("SELECT COUNT(*) FROM players WHERE season = '2024'").fetchone()[0], 
          True))
    print("✅ Added 2024 data snapshot record")
    
    # Create historical player stats table for tracking changes over time
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_stats_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            team TEXT NOT NULL,
            season TEXT NOT NULL,
            snapshot_date TEXT NOT NULL,
            position TEXT,
            minutes_played INTEGER,
            goals INTEGER,
            assists INTEGER,
            shots INTEGER,
            shots_on_target INTEGER,
            fouls_won INTEGER,
            conference TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (season, snapshot_date) REFERENCES data_snapshots(season, snapshot_date)
        )
    """)
    print("✅ Created player_stats_history table")
    
    # Create seasons metadata table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seasons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            is_active BOOLEAN DEFAULT FALSE,
            data_collection_active BOOLEAN DEFAULT FALSE
        )
    """)
    print("✅ Created seasons metadata table")
    
    # Add 2024 and 2025 seasons
    cursor.execute("""
        INSERT OR REPLACE INTO seasons 
        (season, display_name, start_date, end_date, is_active, data_collection_active)
        VALUES 
        ('2024', '2024-25 Season', '2024-08-22', '2024-12-16', FALSE, FALSE),
        ('2025', '2025-26 Season', '2025-08-15', '2025-12-15', FALSE, FALSE)
    """)
    print("✅ Added season metadata")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Database schema updated successfully!")
    print("ℹ️  Your current website will continue working exactly as before")
    print("ℹ️  All existing 2024 data is preserved and labeled properly")

if __name__ == "__main__":
    add_season_tracking_schema()
