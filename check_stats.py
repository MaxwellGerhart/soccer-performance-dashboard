import sqlite3

conn = sqlite3.connect('data/soccer.db')
cursor = conn.cursor()

# Get some basic statistics
cursor.execute("SELECT COUNT(*) FROM events")
total_events = cursor.fetchone()[0]
print(f"Total events: {total_events}")

cursor.execute("SELECT COUNT(DISTINCT team_name) FROM events WHERE team_name IS NOT NULL")
total_teams = cursor.fetchone()[0]
print(f"Total teams: {total_teams}")

cursor.execute("SELECT COUNT(DISTINCT player_name) FROM events WHERE player_name IS NOT NULL")
total_players = cursor.fetchone()[0]
print(f"Total players: {total_players}")

cursor.execute("SELECT COUNT(DISTINCT type_name) FROM events")
total_event_types = cursor.fetchone()[0]
print(f"Total event types: {total_event_types}")

# Get top event types
cursor.execute("SELECT type_name, COUNT(*) as count FROM events GROUP BY type_name ORDER BY count DESC LIMIT 10")
top_events = cursor.fetchall()
print("\nTop 10 event types:")
for event, count in top_events:
    print(f"  {event}: {count}")

# Check for goals
cursor.execute("SELECT COUNT(*) FROM events WHERE type_name = 'Shot' AND shot_outcome_name = 'Goal'")
goals = cursor.fetchone()[0]
print(f"\nTotal goals: {goals}")

conn.close()
