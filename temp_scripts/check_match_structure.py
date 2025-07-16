import sqlite3

conn = sqlite3.connect('data/soccer.db')
cursor = conn.cursor()

print("=== FINDING MATCH-LEVEL DATA FOR BETTER DEFENSIVE METRICS ===\n")

# Check for match or game identifiers
cursor.execute("PRAGMA table_info(events)")
columns = [col[1] for col in cursor.fetchall()]
match_related = [col for col in columns if any(word in col.lower() for word in ['match', 'game', 'id'])]
print(f"Potential match-related columns: {match_related}")

# Check if we have match IDs or similar
cursor.execute("SELECT DISTINCT id FROM events LIMIT 10")
ids = [row[0] for row in cursor.fetchall()]
print(f"Sample IDs: {ids[:5]}")

# Check for patterns in period/team combinations that might indicate matches
cursor.execute("""
    SELECT 
        period,
        COUNT(DISTINCT team_name) as teams_in_period,
        COUNT(DISTINCT possession_team_name) as possession_teams,
        MIN(minute) as min_minute,
        MAX(minute) as max_minute
    FROM events 
    WHERE team_name IS NOT NULL
    GROUP BY period
    ORDER BY period
""")
period_data = cursor.fetchall()
print("Period analysis:")
for period, teams, poss_teams, min_min, max_min in period_data:
    print(f"  Period {period}: {teams} teams, {poss_teams} possession teams, minutes {min_min}-{max_min}")

# Try to identify matches by looking at team combinations in the same period/timeframe
cursor.execute("""
    SELECT 
        period,
        minute,
        GROUP_CONCAT(DISTINCT team_name) as teams,
        GROUP_CONCAT(DISTINCT possession_team_name) as possession_teams,
        COUNT(*) as events
    FROM events 
    WHERE team_name IS NOT NULL AND minute BETWEEN 0 AND 10
    GROUP BY period, minute
    HAVING COUNT(DISTINCT team_name) = 2
    ORDER BY period, minute
    LIMIT 20
""")
potential_matches = cursor.fetchall()
print(f"\nPotential match pairings (first 10 minutes):")
for period, minute, teams, poss_teams, events in potential_matches[:10]:
    print(f"  Period {period}, Min {minute}: {teams} ({events} events)")

conn.close()
