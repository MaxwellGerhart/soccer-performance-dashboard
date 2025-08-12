import sqlite3

conn = sqlite3.connect('data/ncaa_soccer.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Database tables:')
for table in tables:
    print(f'  {table[0]}')

# Check if there's a ratings-related table
for table in tables:
    table_name = table[0]
    if 'rating' in table_name.lower():
        print(f'\nColumns in {table_name}:')
        cursor.execute(f'PRAGMA table_info({table_name})')
        columns = cursor.fetchall()
        for col in columns:
            print(f'  {col[1]}')

conn.close()
