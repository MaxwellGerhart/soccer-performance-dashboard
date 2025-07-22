import sqlite3

conn = sqlite3.connect('data/ncaa_soccer.db')
cursor = conn.cursor()

# Check teams currently in Other category
cursor.execute('SELECT DISTINCT team FROM players WHERE conference = ? ORDER BY team', ('Other',))
teams = cursor.fetchall()

print('Teams currently in Other category:')
sun_belt_candidates = []
for team in teams:
    team_name = team[0]
    print(f'  {team_name}')
    # Look for likely Sun Belt teams
    if any(keyword in team_name.lower() for keyword in [
        'georgia southern', 'ga. southern', 'appalachian', 'troy', 'south alabama', 
        'texas state', 'louisiana', 'arkansas state', 'old dominion', 'james madison',
        'southern miss', 'ul monroe', 'ul lafayette'
    ]):
        sun_belt_candidates.append(team_name)

print(f'\nFound {len(sun_belt_candidates)} potential Sun Belt teams:')
for team in sun_belt_candidates:
    print(f'  {team}')

conn.close()
