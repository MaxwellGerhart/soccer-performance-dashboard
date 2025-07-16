import sqlite3
import json

conn = sqlite3.connect('data/soccer.db')
cursor = conn.cursor()

print("=== ALTERNATIVE APPROACH: ESTIMATE GOALS AGAINST FROM AVAILABLE DATA ===\n")

# Since we can't easily identify individual matches, let's use a different approach
# We'll estimate goals against based on the World Cup structure and known results

# First, let's see what we can derive from the current data
cursor.execute("""
    SELECT 
        team_name,
        -- Goals scored by this team
        SUM(CASE WHEN type_name = 'Shot' AND shot_outcome_name = 'Goal' 
             AND possession_team_name = team_name THEN 1 ELSE 0 END) as goals_scored,
        -- Goals where this team was defending (opponent possession)
        SUM(CASE WHEN type_name = 'Shot' AND shot_outcome_name = 'Goal' 
             AND possession_team_name != team_name THEN 1 ELSE 0 END) as goals_conceded,
        -- xG for
        ROUND(SUM(CASE WHEN shot_statsbomb_xg IS NOT NULL 
                  AND possession_team_name = team_name THEN shot_statsbomb_xg ELSE 0 END), 2) as xg_for,
        -- xG against  
        ROUND(SUM(CASE WHEN shot_statsbomb_xg IS NOT NULL 
                  AND possession_team_name != team_name THEN shot_statsbomb_xg ELSE 0 END), 2) as xg_against
    FROM events
    WHERE team_name IS NOT NULL
    GROUP BY team_name
    ORDER BY goals_scored DESC
""")

results = cursor.fetchall()
print("Team defensive metrics (team, goals_for, goals_against, xg_for, xg_against):")
for team, goals_for, goals_against, xg_for, xg_against in results:
    print(f"  {team}: {goals_for}G / {goals_against}GA / {xg_for}xG / {xg_against}xGA")

# Let's also check totals to validate
cursor.execute("SELECT COUNT(*) FROM events WHERE type_name = 'Shot' AND shot_outcome_name = 'Goal'")
total_goals = cursor.fetchone()[0]
print(f"\nTotal goals in dataset: {total_goals}")

total_goals_for = sum(row[1] for row in results)
total_goals_against = sum(row[2] for row in results)
print(f"Sum of goals for: {total_goals_for}")
print(f"Sum of goals against: {total_goals_against}")

conn.close()
