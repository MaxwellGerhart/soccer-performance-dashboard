import sqlite3

conn = sqlite3.connect('data/soccer.db')
cursor = conn.cursor()

# Check defensive action types
cursor.execute("""
    SELECT type_name, COUNT(*) 
    FROM events 
    WHERE type_name IN ('Duel', 'Interception', 'Ball Recovery', 'Clearance', 'Foul Committed') 
    GROUP BY type_name 
    ORDER BY COUNT(*) DESC
""")
results = cursor.fetchall()
print('Defensive Actions:')
for row in results:
    print(f'  {row[0]}: {row[1]}')

# Check if there are any duel-related columns
cursor.execute("PRAGMA table_info(events)")
columns = [col[1] for col in cursor.fetchall()]
duel_columns = [col for col in columns if 'duel' in col.lower()]
print(f'\nDuel-related columns: {duel_columns}')

# Check duel outcomes
cursor.execute("SELECT DISTINCT duel_outcome_name FROM events WHERE duel_outcome_name IS NOT NULL")
duel_outcomes = [row[0] for row in cursor.fetchall()]
print(f'Duel outcomes: {duel_outcomes}')

conn.close()
