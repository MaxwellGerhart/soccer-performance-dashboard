"""
NCAA Soccer Data Collection System
Converted from Player Data.ipynb for production use
"""

import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import json
import os
import requests
from bs4 import BeautifulSoup
import re
import unidecode
from rapidfuzz import process, fuzz
from datetime import datetime, timedelta
import sqlite3
from collections import Counter

class NCAADataCollector:
    def __init__(self, season='2025', division='d1'):
        self.season = season
        self.division = division
        self.base_data_dir = f'data/{season}'
        os.makedirs(f'{self.base_data_dir}/weekly_updates', exist_ok=True)
        
    def get_game_ids(self, day):
        """Get game IDs for a specific day"""
        url = f"https://www.ncaa.com/scoreboard/soccer-men/{self.division}/{self.season}/{day}"
        print(f"Fetching games for {day}: {url}")

        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                game_links = soup.find_all('a', class_='gamePod-link')
                hrefs = [link['href'] for link in game_links]
                game_ids = [href.split('/')[2] for href in hrefs]
                print(f"Found {len(game_ids)} games")
                return game_ids
            else:
                print(f"Failed to retrieve webpage. Status code: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error fetching game IDs for {day}: {e}")
            return []

    def clean_name(self, name):
        """Clean and standardize player names"""
        if not name:
            return ""
        if ', ' in name:
            name = ' '.join(name.split(', ')[::-1])  # Reverse names if in "Last, First" format
        name = unidecode.unidecode(name)  # Remove accents and special characters
        name = name.strip().title()  # Strip extra spaces and standardize capitalization
        return name

    def clean_data(self, data):
        """Extract and clean player data from game JSON"""
        home_id = str(data['meta']['teams'][0]['id'])
        away_id = str(data['meta']['teams'][1]['id'])
        home_name = data['meta']['teams'][0]['shortName']
        away_name = data['meta']['teams'][1]['shortName']

        players_list = []

        for team in data['teams']:
            team_id = str(team['teamId'])
            
            if team_id == home_id:
                team_type = 'Home'
                team_name = home_name
            elif team_id == away_id:
                team_type = 'Away'
                team_name = away_name
            else:
                print(f"Unexpected Team ID: {team_id}")
                continue

            for player in team['playerStats']:
                full_name = f"{player['firstName']} {player['lastName']}"
                full_name = self.clean_name(full_name)

                position = player['position']
                minutes_played = int(player['minutesPlayed'])
                goals = int(player['goals'])
                assists = int(player['assists'])
                shots = int(player['shots'])
                shots_on_target = int(player['shotsOnGoal'])

                players_list.append({
                    'Name': full_name,
                    'Position': position,
                    'Minutes Played': minutes_played,
                    'Goals': goals,
                    'Assists': assists,
                    'Shots': shots,
                    'Shots On Target': shots_on_target,
                    'Team': team_name
                })
                
        return players_list

    def collect_data(self, game_ids):
        """Collect player data from multiple games"""
        players_data = []

        for game_id in game_ids:
            data = None

            try:
                response = requests.get(f'https://data.ncaa.com/casablanca/game/{game_id}/boxscore.json')
                response.raise_for_status()
                data = response.json()

            except requests.exceptions.RequestException as e:
                print(f"Error fetching data via requests for game ID {game_id}: {e}")

                try:
                    result = os.popen(
                        f'curl https://data.ncaa.com/casablanca/game/{game_id}/boxscore.json'
                    ).read()
                    data = json.loads(result)

                except Exception as e:
                    print(f"Error fetching data for game ID {game_id} using curl: {e}")
                    continue

            if data is None or 'meta' not in data:
                print(f"Error: 'meta' key not found in data for game ID {game_id}")
                continue

            cleaned_data = self.clean_data(data)
            players_data.append(cleaned_data)

        return players_data

    def categorize_event(self, event):
        """Categorize play-by-play events"""
        if 'Goal by' in event:
            return 'Goal'
        elif 'Shot by' in event:
            return 'Shot'
        elif 'Foul on' in event:
            return 'Foul'
        elif 'Corner kick' in event:
            return 'Corner Kick'
        elif 'Offside' in event:
            return 'Offside'
        else:
            return 'Other'

    def extract_player(self, event):
        """Extract player name from play-by-play event"""
        pattern = r'\b[A-Z][a-z]+,?\s*[A-Z][a-z]+'
        matches = re.findall(pattern, event)
        return matches[0] if matches else None

    def collect_fouls_won(self, game_ids):
        """Collect fouls won data from play-by-play"""
        foul_data = []
        
        for game_id in game_ids:
            data = None

            try:
                response = requests.get(f'https://data.ncaa.com/casablanca/game/{game_id}/pbp.json')
                response.raise_for_status()
                data = response.json()

            except requests.exceptions.RequestException as e:
                print(f"Error fetching PBP data via requests for game ID {game_id}: {e}")

                try:
                    result = os.popen(
                        f'curl https://data.ncaa.com/casablanca/game/{game_id}/pbp.json'
                    ).read()
                    data = json.loads(result)

                except Exception as e:
                    print(f"Error fetching PBP data for game ID {game_id} using curl: {e}")
                    continue

            if not data or 'meta' not in data or 'periods' not in data:
                print(f"Invalid PBP data for game ID {game_id}")
                continue

            home = data['meta']['teams'][0]['shortName']
            away = data['meta']['teams'][1]['shortName']

            events = []
            score = '0-0'
            for period in data['periods']:
                for play in period['playStats']:
                    score = play['score'] if play['score'] else score
                    time = play['time']

                    if play['visitorText']:
                        team = 1
                        event = play['visitorText']
                    else:
                        team = 0
                        event = play['homeText']

                    event_details = {
                        'Score': score,
                        'Time': time,
                        'Event': event,
                        'Team': team
                    }
                    events.append(event_details)

            df = pd.DataFrame(events)
            df['Name'] = df['Event'].apply(self.extract_player)
            df['Name'] = df['Name'].apply(self.clean_name)
            df['Event_Type'] = df['Event'].apply(self.categorize_event)
            df['Team'] = df['Team'].apply(lambda x: home if x == 0 else away)
            df['IsFoul'] = df['Event'].str.contains('Foul', case=False)

            foul_df = df[df['IsFoul']]
            foul_summary = foul_df.groupby(['Name', 'Team']).size().reset_index(name='Fouls')
            foul_data.append(foul_summary)

        if foul_data:
            all_fouls = pd.concat(foul_data, ignore_index=True)
            return all_fouls
        else:
            return pd.DataFrame(columns=['Name', 'Team', 'Fouls'])

    def preprocess_name(self, name):
        """Preprocess names for fuzzy matching"""
        if not name:
            return ""
        name = unidecode.unidecode(name).strip().lower()
        return name

    def create_name_mapping(self, *name_lists, similarity_threshold=90):
        """Create unified name mapping for consistency"""
        all_names = set()
        for names in name_lists:
            all_names.update(self.preprocess_name(name) for name in names)
        
        standardized_names = {}
        unique_processed_names = list(all_names)

        for name in unique_processed_names:
            match = process.extractOne(name, standardized_names.keys(), scorer=fuzz.WRatio)
            if match and match[1] > similarity_threshold:
                standardized_names[name] = standardized_names[match[0]]
            else:
                standardized_names[name] = name

        return standardized_names

    def apply_name_mapping(self, names, name_mapping):
        """Apply name mapping to standardize names"""
        return [name_mapping[self.preprocess_name(name)] for name in names]

    def dominant_position(self, pos):
        """Determine dominant position from position string"""
        if pd.isna(pos) or not isinstance(pos, str) or len(pos) == 0:
            return "Unknown"
        
        position_keywords = {
            'Midfielder': ['M', 'Midfielder'],
            'Defender': ['D', 'Defender'],
            'Forward': ['F', 'Forward'],
            'Goalkeeper': ['G', 'Goalkeeper']
        }
        
        position_counts = {
            position: sum(pos.upper().count(keyword.upper()) for keyword in keywords)
            for position, keywords in position_keywords.items()
        }
        
        if all(count == 0 for count in position_counts.values()):
            return "Unknown"
        
        dominant_position = max(position_counts, key=position_counts.get)
        return dominant_position

    def update_fouls_for_subset_names(self, df, fouls):
        """Update fouls for players with partial name matches"""
        df = df.copy()
        for idx, row in df.iterrows():
            if row['Fouls Won'] == 0:
                matching_fouls = fouls[
                    (fouls['Team'] == row['Team']) &
                    (fouls['Name'].apply(lambda x: row['Name'] in x or x in row['Name']))
                ]
                if not matching_fouls.empty:
                    total_fouls = matching_fouls['Fouls'].sum()
                    df.at[idx, 'Fouls Won'] = total_fouls
        return df

    def collect_season_data(self, start_date, end_date, description=""):
        """Collect data for a date range (main collection method)"""
        print(f"🏈 Starting data collection for {self.season} season")
        print(f"📅 Date range: {start_date} to {end_date}")
        
        # Generate date range
        date_range = pd.date_range(start=start_date, end=end_date)
        time_range = date_range.strftime('%m/%d').tolist()
        
        # Initialize storage
        dfs = []
        fouls = []
        
        print(f"🔄 Processing {len(time_range)} days...")
        
        # Collect data for each day
        for day in time_range:
            try:
                game_ids = self.get_game_ids(day)
                if not game_ids:
                    print(f"No games found for {day}")
                    continue
                    
                players_data = self.collect_data(game_ids)
                fouls_won = self.collect_fouls_won(game_ids)

                flattened_data = [player for game in players_data for player in game]
                
                df = pd.DataFrame(flattened_data)
                fouls.append(fouls_won)
                dfs.append(df)
                print(f"✅ {day} completed - {len(game_ids)} games, {len(flattened_data)} player records")
                
            except Exception as e:
                print(f"❌ Error processing {day}: {e}")
                continue

        if not dfs:
            print("❌ No data collected")
            return None, None
            
        # Concatenate all data
        print("🔄 Consolidating data...")
        dfs = pd.concat(dfs, ignore_index=True)
        fouls = pd.concat(fouls, ignore_index=True)

        # Clean and standardize names
        dfs['Name'] = dfs['Name'].apply(self.clean_name)
        fouls['Name'] = fouls['Name'].apply(self.clean_name)

        # Create unified name mapping
        all_names = list(dfs['Name']) + list(fouls['Name'])
        name_mapping = self.create_name_mapping(all_names)

        # Apply name standardization
        dfs['Name'] = self.apply_name_mapping(dfs['Name'], name_mapping)
        fouls['Name'] = self.apply_name_mapping(fouls['Name'], name_mapping)

        # Group and aggregate data
        final_df = dfs.groupby(['Name', 'Team'], as_index=False).sum()
        fouls = fouls.groupby(['Name', 'Team'], as_index=False).sum()

        # Filter valid names
        player_stats = final_df[final_df['Name'].notnull() & (final_df['Name'].str.strip() != '')]

        # Merge fouls data
        player_stats = pd.merge(player_stats, fouls, on=['Name', 'Team'], how='left', suffixes=('', '_fouls'))
        player_stats['Fouls Won'] = player_stats['Fouls'].fillna(0)

        # Update fouls for subset name matches
        player_stats = self.update_fouls_for_subset_names(player_stats, fouls)

        # Standardize positions
        player_stats['Position'] = player_stats['Position'].apply(self.dominant_position)
        player_stats['Name'] = player_stats['Name'].apply(lambda x: x.title())

        # Final column selection
        player_stats = player_stats[['Name', 'Team', 'Position', 'Minutes Played', 'Goals', 'Assists', 'Shots', 'Shots On Target', 'Fouls Won']]

        print(f"✅ Data collection completed!")
        print(f"📊 Total players: {len(player_stats)}")
        print(f"🏟️  Total teams: {player_stats['Team'].nunique()}")
        
        return player_stats, description

    def save_data(self, player_stats, snapshot_date, description=""):
        """Save collected data to files and database"""
        if player_stats is None:
            print("❌ No data to save")
            return None
            
        # Create weekly folder
        week_dir = f'{self.base_data_dir}/weekly_updates/{snapshot_date}'
        os.makedirs(week_dir, exist_ok=True)
        
        # Save CSV
        csv_path = f'{week_dir}/ncaa_players_{self.season}_{snapshot_date.replace("-", "")}.csv'
        player_stats.to_csv(csv_path, index=False)
        print(f"💾 Saved CSV: {csv_path}")
        
        return week_dir, csv_path


# Test function for 2024 data (safe to run)
def test_with_2024_data():
    """Test the collector with a small 2024 date range"""
    print("🧪 Testing data collector with 2024 data...")
    
    collector = NCAADataCollector(season='2024', division='d1')
    
    # Test with just a few days from 2024
    start_date = '2024-11-01'
    end_date = '2024-11-03'
    
    player_stats, description = collector.collect_season_data(start_date, end_date, "Test collection")
    
    if player_stats is not None:
        print(f"✅ Test successful! Collected {len(player_stats)} player records")
        print("\nSample data:")
        print(player_stats.head())
        
        # Save test data
        test_dir, csv_path = collector.save_data(player_stats, '2024-11-test', 'Test collection')
        print(f"📁 Test data saved to: {test_dir}")
    else:
        print("❌ Test failed - no data collected")

if __name__ == "__main__":
    test_with_2024_data()
