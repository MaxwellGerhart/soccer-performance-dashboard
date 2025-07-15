import sqlite3

conn = sqlite3.connect('data/soccer.db')
cursor = conn.cursor()

# Check duel types
cursor.execute("SELECT DISTINCT duel_type_name FROM events WHERE duel_type_name IS NOT NULL")
duel_types = [row[0] for row in cursor.fetchall()]
print(f'Duel types: {duel_types}')

# Check successful duels by type
cursor.execute("""
    SELECT duel_type_name, duel_outcome_name, COUNT(*) 
    FROM events 
    WHERE duel_type_name IS NOT NULL AND duel_outcome_name IS NOT NULL
    GROUP BY duel_type_name, duel_outcome_name 
    ORDER BY duel_type_name, COUNT(*) DESC
""")
results = cursor.fetchall()
print('\nDuel types and outcomes:')
for row in results:
    print(f'  {row[0]} - {row[1]}: {row[2]}')

# Check top players with successful duels (tackles)
cursor.execute("""
    SELECT player_name, COUNT(*) as successful_duels
    FROM events 
    WHERE type_name = 'Duel' 
    AND duel_outcome_name IN ('Won', 'Success In Play', 'Success Out')
    AND player_name IS NOT NULL
    GROUP BY player_name 
    ORDER BY successful_duels DESC 
    LIMIT 10
""")
top_tacklers = cursor.fetchall()
print('\nTop 10 players with successful duels (tackles):')
for row in top_tacklers:
    print(f'  {row[0]}: {row[1]}')

conn.close()
