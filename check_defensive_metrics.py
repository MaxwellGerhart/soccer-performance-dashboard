import sqlite3

conn = sqlite3.connect('data/soccer.db')
cursor = conn.cursor()

print("=== CHECKING GOALS AGAINST AND XG AGAINST DATA ===\n")

# Let's see the structure of match data
cursor.execute("""
    SELECT DISTINCT team_name, possession_team_name, type_name, shot_outcome_name
    FROM events 
    WHERE type_name = 'Shot' AND shot_outcome_name = 'Goal'
    LIMIT 20
""")
goal_data = cursor.fetchall()
print("Sample goal data (team_name, possession_team_name, type_name, outcome):")
for row in goal_data:
    print(f"  {row}")

print("\n" + "="*50)

# Check if we can identify goals against by looking at possession vs team
cursor.execute("""
    SELECT 
        team_name as defending_team,
        COUNT(*) as goals_conceded
    FROM events 
    WHERE type_name = 'Shot' 
    AND shot_outcome_name = 'Goal'
    AND possession_team_name != team_name
    GROUP BY team_name
    ORDER BY goals_conceded DESC
""")
goals_against_data = cursor.fetchall()
print("Goals against by team (defending team):")
for team, goals in goals_against_data:
    print(f"  {team}: {goals} goals conceded")

print("\n" + "="*50)

# Check xG against
cursor.execute("""
    SELECT 
        team_name as defending_team,
        ROUND(SUM(shot_statsbomb_xg), 2) as xg_against
    FROM events 
    WHERE type_name = 'Shot' 
    AND shot_statsbomb_xg IS NOT NULL
    AND possession_team_name != team_name
    GROUP BY team_name
    ORDER BY xg_against DESC
""")
xg_against_data = cursor.fetchall()
print("xG against by team (defending team):")
for team, xg in xg_against_data:
    print(f"  {team}: {xg} xG conceded")

conn.close()
