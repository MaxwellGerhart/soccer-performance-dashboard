import pandas as pd
import sqlite3

def update_conferences_from_csv():
    """Update player conferences based on actual data from ncaa_mens_scores_2024.csv"""
    
    # Read the scores CSV to get team-conference mappings
    df = pd.read_csv('data/ncaa_mens_scores_2024.csv')
    
    # Create a mapping from team names to conferences
    team_conferences = {}
    
    # Get conferences from home teams
    for _, row in df.iterrows():
        home_team = row['home_team']
        home_conf = row['home_team_conference']
        away_team = row['away_team']
        away_conf = row['away_team_conference']
        
        # Only include D1 teams (exclude "Not D1")
        if home_conf != 'Not D1' and pd.notna(home_conf):
            team_conferences[home_team] = home_conf
            
        if away_conf != 'Not D1' and pd.notna(away_conf):
            team_conferences[away_team] = away_conf
    
    print(f"Found {len(team_conferences)} teams with conference data")
    
    # Show conference distribution
    conf_counts = {}
    for conf in team_conferences.values():
        conf_counts[conf] = conf_counts.get(conf, 0) + 1
    
    print("\nConference distribution from CSV:")
    for conf, count in sorted(conf_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {conf}: {count} teams")
    
    # Update the database
    conn = sqlite3.connect('data/ncaa_soccer.db')
    cursor = conn.cursor()
    
    # Reset all conferences to NULL first
    cursor.execute("UPDATE players SET conference = NULL")
    
    # Update players with conference information
    updated_count = 0
    for team, conference in team_conferences.items():
        cursor.execute("UPDATE players SET conference = ? WHERE team = ?", (conference, team))
        updated_count += cursor.rowcount
    
    # Set remaining teams to "Other" conference
    cursor.execute("UPDATE players SET conference = 'Other' WHERE conference IS NULL")
    other_count = cursor.rowcount
    
    conn.commit()
    
    print(f"\nUpdated {updated_count} players with known conferences")
    print(f"Set {other_count} players to 'Other' conference")
    
    # Show final conference distribution in database
    cursor.execute("SELECT conference, COUNT(*) as player_count FROM players GROUP BY conference ORDER BY player_count DESC")
    conferences = cursor.fetchall()
    print("\nFinal conference distribution in database:")
    for conf, count in conferences:
        print(f"  {conf}: {count} players")
    
    # Show some examples of teams not found
    cursor.execute("SELECT DISTINCT team FROM players WHERE conference = 'Other' LIMIT 10")
    other_teams = cursor.fetchall()
    print(f"\nSample teams marked as 'Other' (not found in CSV):")
    for team in other_teams:
        print(f"  {team[0]}")
    
    conn.close()

if __name__ == "__main__":
    update_conferences_from_csv()
