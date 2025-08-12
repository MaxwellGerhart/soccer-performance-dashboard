import sqlite3
import pandas as pd

conn = sqlite3.connect('data/ncaa_soccer.db')

# Check Elijah Jackson
elijah = pd.read_sql_query("SELECT Name, Team, Position, MAX FROM players WHERE Name = 'Elijah Jackson'", conn)
print("Elijah Jackson after fix:")
print(elijah.to_string(index=False))

# Check top defenders 
top_def = pd.read_sql_query("SELECT Name, Team, MAX FROM players WHERE Position = 'Defender' ORDER BY MAX DESC LIMIT 5", conn)
print("\nTop 5 defenders after fix:")
print(top_def.to_string(index=False))

conn.close()
