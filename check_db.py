import sqlite3

conn = sqlite3.connect('data/ncaa_soccer.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables available:", [table[0] for table in tables])

# Check players table structure
cursor.execute("PRAGMA table_info(players)")
columns = cursor.fetchall()
print("\nPlayers table columns:", [col[1] for col in columns])

# Check sample data
cursor.execute("SELECT * FROM players LIMIT 3")
sample_data = cursor.fetchall()
print("\nSample player data:")
for row in sample_data:
    print(row)

# Check if there's team/conference data in other files
import os
if os.path.exists('data'):
    print("\nFiles in data directory:")
    for file in os.listdir('data'):
        print(f"  {file}")

conn.close()
