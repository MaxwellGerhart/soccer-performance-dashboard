import sqlite3
from player_traits import PlayerTraitCalculator

def save_traits_to_db():
    """Calculate and save player traits to the database"""
    
    # Create traits table
    conn = sqlite3.connect('data/soccer.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_traits (
            player_name TEXT PRIMARY KEY,
            spatial_awareness_score REAL,
            decision_efficiency_index REAL,
            technical_execution_quotient REAL,
            composite_score REAL,
            total_events INTEGER,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Calculate traits
    calculator = PlayerTraitCalculator()
    traits = calculator.calculate_all_traits(limit=100)
    calculator.close()
    
    # Save to database
    for trait in traits:
        cursor.execute('''
            INSERT OR REPLACE INTO player_traits 
            (player_name, spatial_awareness_score, decision_efficiency_index, 
             technical_execution_quotient, composite_score, total_events)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            trait['player_name'],
            trait['spatial_awareness_score'],
            trait['decision_efficiency_index'],
            trait['technical_execution_quotient'],
            trait['composite_score'],
            trait['total_events']
        ))
    
    conn.commit()
    conn.close()
    
    print(f"Saved {len(traits)} player traits to database")

if __name__ == "__main__":
    save_traits_to_db()
