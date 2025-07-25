"""
Weekly Data Management System for NCAA Soccer Dashboard
This script will be used when the 2025 season starts
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta
from ncaa_data_collector import NCAADataCollector

class SeasonDataManager:
    def __init__(self):
        self.db_path = 'data/ncaa_soccer.db'
        
    def get_db_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def is_season_active(self, season):
        """Check if data collection is active for a season"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT data_collection_active FROM seasons 
            WHERE season = ?
        """, (season,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result and result[0]
    
    def activate_season(self, season):
        """Activate data collection for a season"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Deactivate all other seasons
        cursor.execute("UPDATE seasons SET is_active = FALSE, data_collection_active = FALSE")
        
        # Activate the specified season
        cursor.execute("""
            UPDATE seasons 
            SET is_active = TRUE, data_collection_active = TRUE 
            WHERE season = ?
        """, (season,))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Activated data collection for {season} season")
    
    def import_weekly_data(self, player_stats, season, snapshot_date, description=""):
        """Import weekly data to database"""
        if player_stats is None or len(player_stats) == 0:
            print("❌ No data to import")
            return False
            
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Add data snapshot record
            cursor.execute("""
                INSERT OR REPLACE INTO data_snapshots 
                (season, snapshot_date, description, total_players, is_current)
                VALUES (?, ?, ?, ?, TRUE)
            """, (season, snapshot_date, description, len(player_stats)))
            
            # Mark previous snapshots as not current for this season
            cursor.execute("""
                UPDATE data_snapshots 
                SET is_current = FALSE 
                WHERE season = ? AND snapshot_date != ?
            """, (season, snapshot_date))
            
            # Remove existing player data for this snapshot (if updating)
            cursor.execute("""
                DELETE FROM players 
                WHERE season = ? AND data_date = ?
            """, (season, snapshot_date))
            
            # Insert new player data
            for _, player in player_stats.iterrows():
                cursor.execute("""
                    INSERT INTO players 
                    (name, team, position, minutes_played, goals, assists, shots, 
                     shots_on_target, fouls_won, season, data_date, conference)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    player['Name'], player['Team'], player['Position'],
                    player['Minutes Played'], player['Goals'], player['Assists'],
                    player['Shots'], player['Shots On Target'], player['Fouls Won'],
                    season, snapshot_date, None  # Conference will be updated separately
                ))
            
            # Also insert into history table
            for _, player in player_stats.iterrows():
                cursor.execute("""
                    INSERT OR REPLACE INTO player_stats_history 
                    (player_name, team, season, snapshot_date, position,
                     minutes_played, goals, assists, shots, shots_on_target, fouls_won)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    player['Name'], player['Team'], season, snapshot_date,
                    player['Position'], player['Minutes Played'], player['Goals'],
                    player['Assists'], player['Shots'], player['Shots On Target'],
                    player['Fouls Won']
                ))
            
            conn.commit()
            print(f"✅ Successfully imported {len(player_stats)} players for {season} - {snapshot_date}")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error importing data: {e}")
            return False
        finally:
            conn.close()
    
    def update_conferences(self, season, snapshot_date):
        """Update conference information from scores data"""
        try:
            # Try to read scores CSV for the season
            scores_file = f'data/{season}/ncaa_mens_scores_{season}.csv'
            if not os.path.exists(scores_file):
                print(f"⚠️  Scores file not found: {scores_file}")
                return False
                
            from update_conferences_from_csv import update_conferences_from_csv
            # This would need to be modified to work with specific season/date
            update_conferences_from_csv()
            print(f"✅ Updated conferences for {season} - {snapshot_date}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating conferences: {e}")
            return False
    
    def run_weekly_collection(self, season='2025'):
        """Run weekly data collection (when season is active)"""
        if not self.is_season_active(season):
            print(f"⚠️  Data collection not active for {season} season")
            return False
            
        print(f"🏈 Starting weekly collection for {season} season...")
        
        # Calculate date range (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        snapshot_date = end_date.strftime('%Y-%m-%d')
        
        # Initialize collector
        collector = NCAADataCollector(season=season, division='d1')
        
        try:
            # Collect data
            player_stats, description = collector.collect_season_data(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d'),
                f"Weekly update - {snapshot_date}"
            )
            
            if player_stats is not None:
                # Save to files
                week_dir, csv_path = collector.save_data(player_stats, snapshot_date, description)
                
                # Import to database
                success = self.import_weekly_data(player_stats, season, snapshot_date, description)
                
                if success:
                    # Update conferences
                    self.update_conferences(season, snapshot_date)
                    
                    print(f"🎉 Weekly collection completed successfully!")
                    print(f"📊 Processed {len(player_stats)} players")
                    return True
                    
        except Exception as e:
            print(f"❌ Weekly collection failed: {e}")
            
        return False
    
    def prepare_for_2025_season(self):
        """Prepare the system for 2025 season data collection"""
        print("🔧 Preparing for 2025 season...")
        
        # Create directory structure
        os.makedirs('data/2025/weekly_updates', exist_ok=True)
        os.makedirs('data/2025/conference_data', exist_ok=True)
        
        # Update season status (but don't activate yet)
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE seasons 
            SET start_date = '2025-08-15', end_date = '2025-12-15'
            WHERE season = '2025'
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ System prepared for 2025 season")
        print("ℹ️  Data collection will begin when season is manually activated")
    
    def get_season_summary(self):
        """Get summary of all seasons and their data"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.season, s.display_name, s.is_active, s.data_collection_active,
                   COUNT(ds.id) as snapshots,
                   MAX(ds.total_players) as max_players
            FROM seasons s
            LEFT JOIN data_snapshots ds ON s.season = ds.season
            GROUP BY s.season
            ORDER BY s.season DESC
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        print("\n📊 Season Summary:")
        print("-" * 80)
        for row in results:
            season, display_name, is_active, data_active, snapshots, max_players = row
            status = "🟢 Active" if is_active else "⚪ Inactive"
            collection = "📡 Collecting" if data_active else "⏸️  Paused"
            print(f"{season} ({display_name}): {status} | {collection} | {snapshots or 0} snapshots | {max_players or 0} max players")


# Command line interface
def main():
    import sys
    
    manager = SeasonDataManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python weekly_data_manager.py summary")
        print("  python weekly_data_manager.py prepare-2025")
        print("  python weekly_data_manager.py activate-2025")
        print("  python weekly_data_manager.py collect-weekly [season]")
        return
    
    command = sys.argv[1]
    
    if command == 'summary':
        manager.get_season_summary()
        
    elif command == 'prepare-2025':
        manager.prepare_for_2025_season()
        
    elif command == 'activate-2025':
        manager.activate_season('2025')
        
    elif command == 'collect-weekly':
        season = sys.argv[2] if len(sys.argv) > 2 else '2025'
        manager.run_weekly_collection(season)
        
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
