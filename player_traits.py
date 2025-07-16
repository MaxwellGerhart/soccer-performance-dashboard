import sqlite3
import json
import numpy as np
import math
from collections import defaultdict
from datetime import datetime

class PlayerTraitCalculator:
    """Calculate advanced player traits using StatsBomb data"""
    
    def __init__(self, db_path='data/soccer.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
    def parse_location(self, location_str):
        """Parse location string to coordinates"""
        if not location_str:
            return None
        try:
            # Remove brackets and split by comma
            coords = location_str.strip('[]').split(',')
            if len(coords) >= 2:
                return [float(coords[0].strip()), float(coords[1].strip())]
        except:
            pass
        return None
    
    def calculate_distance(self, pos1, pos2):
        """Calculate Euclidean distance between two positions"""
        if not pos1 or not pos2:
            return None
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def parse_timestamp(self, timestamp_str):
        """Parse timestamp string to seconds"""
        if not timestamp_str:
            return None
        try:
            # Format: "00:00:12.345"
            parts = timestamp_str.split(':')
            if len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
        except:
            pass
        return None
    
    def get_player_minutes_played(self, player_name):
        """Estimate minutes played for a player (simplified)"""
        self.cursor.execute("""
            SELECT COUNT(DISTINCT CONCAT(CAST(period AS TEXT), '_', CAST(minute AS TEXT))) 
            FROM events 
            WHERE player_name = ? AND type_name IN ('Pass', 'Shot', 'Dribble', 'Tackle', 'Carry')
        """, (player_name,))
        
        unique_minutes = self.cursor.fetchone()[0]
        return max(90, unique_minutes)  # Assume at least 90 minutes if low count
    
    def calculate_spatial_awareness_score(self, player_name):
        """
        Trait 1: Spatial Awareness Score (SAS)
        - Average distance to nearest opponent when receiving a pass
        - Receptions between defensive lines
        - Forward body orientation percentage
        """
        
        # Get all ball receipts for the player
        self.cursor.execute("""
            SELECT location, pass_angle, pass_length, minute, second
            FROM events 
            WHERE player_name = ? AND type_name = 'Ball Receipt*'
            AND location IS NOT NULL
        """, (player_name,))
        
        receipts = self.cursor.fetchall()
        
        if not receipts:
            return 0.0
        
        total_distance = 0
        valid_receipts = 0
        forward_oriented = 0
        
        for location_str, pass_angle, pass_length, minute, second in receipts:
            location = self.parse_location(location_str)
            if not location:
                continue
                
            valid_receipts += 1
            
            # Simplified distance calculation (assuming average opponent distance)
            # In real implementation, you'd use freeze frame data
            avg_distance = 8.0  # Average assumed distance to nearest opponent
            total_distance += avg_distance
            
            # Forward orientation proxy: passes with forward angle
            if pass_angle and pass_angle > -45 and pass_angle < 45:
                forward_oriented += 1
        
        if valid_receipts == 0:
            return 0.0
            
        mean_distance = total_distance / valid_receipts
        forward_orientation_pct = (forward_oriented / valid_receipts) * 100
        
        # Simplified between-the-lines calculation
        # Count receptions in middle third
        between_lines = valid_receipts * 0.3  # Simplified assumption
        minutes_played = self.get_player_minutes_played(player_name)
        between_lines_per_90 = (between_lines / minutes_played) * 90
        
        # Calculate SAS
        sas = (mean_distance * 0.5) + (between_lines_per_90 * 0.3) + (forward_orientation_pct * 0.2)
        
        return round(sas, 2)
    
    def calculate_decision_efficiency_index(self, player_name):
        """
        Trait 2: Decision Efficiency Index (DEI)
        - Average time between receiving and passing
        - Pressured pass completion %
        - Turnovers under pressure per 90
        """
        
        # Get pass sequences (receipt -> pass)
        self.cursor.execute("""
            SELECT timestamp, duration, under_pressure, pass_outcome_name, type_name
            FROM events 
            WHERE player_name = ? AND type_name IN ('Pass', 'Ball Receipt*')
            AND timestamp IS NOT NULL
            ORDER BY timestamp
        """, (player_name,))
        
        events = self.cursor.fetchall()
        
        if not events:
            return 0.0
        
        time_to_pass_values = []
        pressured_passes = 0
        pressured_completed = 0
        turnovers_under_pressure = 0
        
        for i in range(len(events) - 1):
            current_event = events[i]
            next_event = events[i + 1]
            
            # If current is receipt and next is pass
            if current_event[4] == 'Ball Receipt*' and next_event[4] == 'Pass':
                current_time = self.parse_timestamp(current_event[0])
                next_time = self.parse_timestamp(next_event[0])
                
                if current_time and next_time:
                    time_diff = next_time - current_time
                    if time_diff > 0 and time_diff < 10:  # Reasonable time range
                        time_to_pass_values.append(time_diff)
                
                # Check if next pass was under pressure
                if next_event[2]:  # under_pressure
                    pressured_passes += 1
                    if not next_event[3]:  # pass_outcome_name is null (successful)
                        pressured_completed += 1
                    else:
                        turnovers_under_pressure += 1
        
        if not time_to_pass_values:
            return 0.0
        
        avg_time_to_pass = np.mean(time_to_pass_values)
        pressured_completion_pct = (pressured_completed / max(1, pressured_passes)) * 100
        
        minutes_played = self.get_player_minutes_played(player_name)
        turnovers_per_90 = (turnovers_under_pressure / minutes_played) * 90
        
        # Calculate DEI
        dei = ((1 / max(0.1, avg_time_to_pass)) * 0.4) + (pressured_completion_pct * 0.4) - (turnovers_per_90 * 0.2)
        
        return round(dei, 2)
    
    def calculate_technical_execution_quotient(self, player_name):
        """
        Trait 3: Technical Execution Quotient (TEQ)
        - Pass completion percentage
        - Progressive passes per 90
        - Passes into penalty area/final third per 90
        - First touch errors per 90
        """
        
        # Get pass data
        self.cursor.execute("""
            SELECT pass_outcome_name, pass_length, pass_end_location, location
            FROM events 
            WHERE player_name = ? AND type_name = 'Pass'
        """, (player_name,))
        
        passes = self.cursor.fetchall()
        
        # Get miscontrol data (first touch errors)
        self.cursor.execute("""
            SELECT COUNT(*) FROM events 
            WHERE player_name = ? AND type_name = 'Miscontrol'
        """, (player_name,))
        
        miscontrols = self.cursor.fetchone()[0]
        
        if not passes:
            return 0.0
        
        total_passes = len(passes)
        successful_passes = sum(1 for p in passes if not p[0])  # null outcome = success
        progressive_passes = 0
        final_third_passes = 0
        
        for pass_outcome, pass_length, end_location_str, start_location_str in passes:
            # Progressive passes (simplified: passes > 10 yards forward)
            if pass_length and pass_length > 10:
                start_loc = self.parse_location(start_location_str)
                end_loc = self.parse_location(end_location_str)
                if start_loc and end_loc and end_loc[0] > start_loc[0]:  # Forward pass
                    progressive_passes += 1
            
            # Final third passes (simplified: x > 80)
            end_loc = self.parse_location(end_location_str)
            if end_loc and end_loc[0] > 80:
                final_third_passes += 1
        
        pass_completion_pct = (successful_passes / total_passes) * 100
        
        minutes_played = self.get_player_minutes_played(player_name)
        progressive_per_90 = (progressive_passes / minutes_played) * 90
        final_third_per_90 = (final_third_passes / minutes_played) * 90
        miscontrols_per_90 = (miscontrols / minutes_played) * 90
        
        # Calculate TEQ
        teq = (pass_completion_pct * 0.3) + (progressive_per_90 * 0.25) + (final_third_per_90 * 0.25) - (miscontrols_per_90 * 0.2)
        
        return round(teq, 2)
    
    def calculate_all_traits(self, limit=50):
        """Calculate all traits for top players"""
        
        # Get top players by total events
        self.cursor.execute("""
            SELECT player_name, COUNT(*) as total_events
            FROM events 
            WHERE player_name IS NOT NULL
            GROUP BY player_name 
            ORDER BY total_events DESC 
            LIMIT ?
        """, (limit,))
        
        players = self.cursor.fetchall()
        
        results = []
        
        for player_name, total_events in players:
            print(f"Calculating traits for {player_name}...")
            
            sas = self.calculate_spatial_awareness_score(player_name)
            dei = self.calculate_decision_efficiency_index(player_name)
            teq = self.calculate_technical_execution_quotient(player_name)
            
            results.append({
                'player_name': player_name,
                'total_events': total_events,
                'spatial_awareness_score': sas,
                'decision_efficiency_index': dei,
                'technical_execution_quotient': teq,
                'composite_score': round((sas + dei + teq) / 3, 2)
            })
        
        return results
    
    def close(self):
        self.conn.close()

# Example usage
if __name__ == "__main__":
    calculator = PlayerTraitCalculator()
    
    print("=== CALCULATING ADVANCED PLAYER TRAITS ===\n")
    
    # Calculate traits for top 20 players
    traits = calculator.calculate_all_traits(limit=20)
    
    print("\n=== RESULTS ===")
    print(f"{'Player':<30} {'SAS':<6} {'DEI':<6} {'TEQ':<6} {'Composite':<9}")
    print("-" * 60)
    
    # Sort by composite score
    traits.sort(key=lambda x: x['composite_score'], reverse=True)
    
    for trait in traits:
        print(f"{trait['player_name']:<30} {trait['spatial_awareness_score']:<6} {trait['decision_efficiency_index']:<6} {trait['technical_execution_quotient']:<6} {trait['composite_score']:<9}")
    
    calculator.close()
