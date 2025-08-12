import sqlite3

conn = sqlite3.connect('data/ncaa_soccer.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

seasons = cursor.execute('SELECT * FROM seasons ORDER BY season').fetchall()
print('Seasons in database:')
for s in seasons:
    print(f'  {s["season"]}: {s["display_name"]}')

conn.close()
