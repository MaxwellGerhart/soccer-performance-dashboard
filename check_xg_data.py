import sqlite3

conn = sqlite3.connect('data/soccer.db')
cursor = conn.cursor()

print("=== CHECKING xG AND ASSIST DATA ===\n")

# Check for xG data
cursor.execute("SELECT COUNT(*) FROM events WHERE shot_statsbomb_xg IS NOT NULL")
xg_count = cursor.fetchone()[0]
print(f"Events with xG data: {xg_count}")

# Check for assist data
cursor.execute("SELECT COUNT(*) FROM events WHERE pass_goal_assist = 1")
assist_count = cursor.fetchone()[0]
print(f"Events with goal assists: {assist_count}")

cursor.execute("SELECT COUNT(*) FROM events WHERE pass_shot_assist = 1")
shot_assist_count = cursor.fetchone()[0]
print(f"Events with shot assists: {shot_assist_count}")

# Sample xG values
cursor.execute("SELECT player_name, shot_statsbomb_xg FROM events WHERE shot_statsbomb_xg IS NOT NULL LIMIT 10")
xg_samples = cursor.fetchall()
print(f"\nSample xG values:")
for player, xg in xg_samples:
    print(f"  {player}: {xg}")

# Check goals scored
cursor.execute("SELECT COUNT(*) FROM events WHERE type_name = 'Shot' AND shot_outcome_name = 'Goal'")
goals_count = cursor.fetchone()[0]
print(f"\nTotal goals scored: {goals_count}")

# Check own goals
cursor.execute("SELECT COUNT(*) FROM events WHERE type_name = 'Own Goal For'")
own_goals_for = cursor.fetchone()[0]
print(f"Own goals for: {own_goals_for}")

cursor.execute("SELECT COUNT(*) FROM events WHERE type_name = 'Own Goal Against'")
own_goals_against = cursor.fetchone()[0]
print(f"Own goals against: {own_goals_against}")

conn.close()
