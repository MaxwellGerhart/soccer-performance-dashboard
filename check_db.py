import sqlite3

conn = sqlite3.connect('data/soccer.db')
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print("Tables:", tables)

# Check events table structure
if 'events' in tables:
    cursor.execute("PRAGMA table_info(events)")
    columns = cursor.fetchall()
    print("\nEvents table columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

conn.close()
