import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Circle
import sqlite3
import os
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """Load player and team data from CSV files"""
    # Load drafted players list
    with open('data/mls_2025_drafted_players.txt', 'r') as file:
        mls_2025_drafted_players = [line.strip() for line in file]

    # Load player and team data
    player_df = pd.read_csv('data/d1_player_stats.csv')
    team_df = pd.read_csv('data/ncaa_ratings.csv')

    # Clean up data
    player_df = player_df.drop(columns=['Unnamed: 0'])
    team_df = team_df.drop(columns=['Unnamed: 0'])
    player_df = player_df[player_df['Position'] != 'Goalkeeper']
    player_df = player_df[player_df['Minutes Played'] >= 300]

    player_df['Shot Accuracy'] = player_df.apply(
        lambda row: row['Shots On Target'] / row['Shots'] if row['Shots'] > 0 else 0,
        axis=1
    )

    # Merge player and team data
    merged_df = player_df.merge(team_df, on='Team', suffixes=('_player', '_team'))
    
    return merged_df, mls_2025_drafted_players

def calculate_per90_stats(df):
    """Calculate per-90 statistics"""
    per90_stats = ['Goals', 'Assists', 'Shots', 'Shots On Target', 'Fouls Won']
    for stat in per90_stats:
        df[f'{stat}_per90'] = df[stat] / (df['Minutes Played'] / 90)
    return df

def normalize_stats(df):
    """Normalize statistics for rating calculation"""
    df['Norm_Goals'] = df['Goals_per90'] / df['Goals_per90'].max()
    df['Norm_Assists'] = df['Assists_per90'] / df['Assists_per90'].max()
    df['Norm_Shots'] = df['Shots_per90'] / df['Shots_per90'].max()
    df['Norm_Shots_On_Target'] = df['Shots On Target_per90'] / df['Shots On Target_per90'].max()
    df['Norm_Fouls_Won'] = df['Fouls Won_per90'] / df['Fouls Won_per90'].max()
    df['Norm_Minutes_Played'] = df['Minutes Played'] / df['Minutes Played'].max()
    df['Norm_ATT'] = df['ATT'] / df['ATT'].max()
    df['Norm_DEF'] = df['DEF'] / df['DEF'].max()
    
    # Calculate team minutes played percentage
    team_minutes = df.groupby('Team')['Minutes Played'].sum()
    df['Team_Minutes_Played_Percentage'] = df.apply(
        lambda row: row['Minutes Played'] / team_minutes[row['Team']], axis=1
    )
    
    return df

def get_position_weights():
    """Get optimized weights for each position"""
    # These weights are derived from the optimization in the notebook
    return {
        'Forward': {
            'Goals': 0.35,
            'Assists': 0.20,
            'Shots': 0.25,
            'Team_Att': 0.15,
            'Fouls_Won': 0.05
        },
        'Midfielder': {
            'Goals': 0.20,
            'Assists': 0.30,
            'Shots': 0.15,
            'Team_Att_Def': 0.25,
            'Fouls_Won': 0.10
        },
        'Defender': {
            'Goals': 0.05,
            'Assists': 0.15,
            'Shots': 0.10,
            'Team_Def': 0.60,
            'Fouls_Won': 0.10
        }
    }

def calculate_rating(row, weights):
    """Calculate player rating based on position"""
    if row['Position'] == 'Forward':
        return (
            row['Norm_Goals'] * weights['Forward']['Goals'] +
            row['Norm_Assists'] * weights['Forward']['Assists'] +
            row['Norm_Shots'] * weights['Forward']['Shots'] +
            row['Norm_Fouls_Won'] * weights['Forward']['Fouls_Won'] +
            row['Norm_ATT'] * row['Team_Minutes_Played_Percentage'] * weights['Forward']['Team_Att']
        ) * 100
    elif row['Position'] == 'Midfielder':
        return (
            row['Norm_Goals'] * weights['Midfielder']['Goals'] +
            row['Norm_Assists'] * weights['Midfielder']['Assists'] +
            row['Norm_Shots'] * weights['Midfielder']['Shots'] +
            row['Norm_Fouls_Won'] * weights['Midfielder']['Fouls_Won'] +
            ((row['Norm_ATT'] + row['Norm_DEF']) / 2) * row['Team_Minutes_Played_Percentage'] * weights['Midfielder']['Team_Att_Def']
        ) * 100
    elif row['Position'] == 'Defender':
        return (
            row['Norm_Goals'] * weights['Defender']['Goals'] +
            row['Norm_Assists'] * weights['Defender']['Assists'] +
            row['Norm_Shots'] * weights['Defender']['Shots'] +
            row['Norm_Fouls_Won'] * weights['Defender']['Fouls_Won'] +
            row['Norm_DEF'] * row['Team_Minutes_Played_Percentage'] * weights['Defender']['Team_Def']
        ) * 100
    else:
        return 0

def calculate_max_ratings(df):
    """Calculate MAX ratings for all players"""
    weights = get_position_weights()
    
    # Apply the rating calculation
    df['Overall_Rating'] = df.apply(lambda row: calculate_rating(row, weights), axis=1)
    
    # Apply logarithmic scaling to compress rating range
    df['Log_Rating'] = np.log1p(df['Overall_Rating'])
    
    # Normalize ratings to a 0-100 range
    log_rating_min = df['Log_Rating'].min()
    log_rating_max = df['Log_Rating'].max()
    df['MAX'] = (
        (df['Log_Rating'] - log_rating_min) / (log_rating_max - log_rating_min) * 100
    ).astype(int)
    
    return df

def calculate_percentiles_by_position(df):
    """Calculate percentile rankings for radar charts"""
    metrics = ['Goals_per90', 'Assists_per90', 'Shots_per90', 'Shots On Target_per90', 'Fouls Won_per90']
    
    for position in ['Forward', 'Midfielder', 'Defender']:
        position_df = df[df['Position'] == position]
        for metric in metrics:
            percentile_col = f'{metric}_percentile_{position}'
            df[percentile_col] = 0
            if not position_df.empty:
                df.loc[df['Position'] == position, percentile_col] = (
                    position_df[metric].rank(pct=True) * 100
                ).round(1)
    
    return df

def create_radar_chart(player_name, player_data, output_dir='static/radars', force_regenerate=False):
    """Create a professional-looking radar chart for a player"""
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend for faster generation
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    filename = f"{player_name.replace(' ', '_').replace('.', '')}_radar.png"
    filepath = os.path.join(output_dir, filename)
    
    # Check if chart already exists and is recent (unless forced to regenerate)
    if not force_regenerate and os.path.exists(filepath):
        import time
        file_age = time.time() - os.path.getmtime(filepath)
        if file_age < 86400:  # 24 hours in seconds
            return filename
    
    try:
        position = player_data['Position']
        
        # Define comprehensive radar metrics similar to the professional chart
        metrics = [
            'Goals', 'Assists', 'Shots', 'Shots on Target', 
            'Fouls Won'
        ]
        
        values = [
            player_data.get(f'Goals_per90_percentile_{position}', 0),
            player_data.get(f'Assists_per90_percentile_{position}', 0),
            player_data.get(f'Shots_per90_percentile_{position}', 0),
            player_data.get(f'Shots On Target_per90_percentile_{position}', 0),
            player_data.get(f'Fouls Won_per90_percentile_{position}', 0)
        ]
        
        # Ensure all values are numeric
        values = [float(v) if v != 'N/A' and v is not None else 0 for v in values]
        
        # Close the radar chart
        values_plot = values + [values[0]]
        
        # Calculate angles
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles_plot = angles + [angles[0]]
        
        # Create the plot with professional styling
        plt.style.use('default')  # Reset to default style
        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(polar=True), facecolor='white')
        
        # Color scheme similar to the professional chart
        attacking_color = '#4a90a4'  # Teal
        possession_color = '#c7b299'  # Beige
        defending_color = '#c85a5a'  # Red
        
        # Determine primary color based on position
        if position == 'Forward':
            primary_color = attacking_color
            position_desc = "Forward"
        elif position == 'Midfielder':
            primary_color = possession_color
            position_desc = "Midfielder"
        else:
            primary_color = defending_color
            position_desc = "Defender"
        
        # Plot the main radar area
        ax.fill(angles_plot, values_plot, color=primary_color, alpha=0.25)
        ax.plot(angles_plot, values_plot, color=primary_color, linewidth=3, solid_capstyle='round')
        
        # Add dots at each data point
        for angle, value in zip(angles, values):
            ax.plot(angle, value, 'o', color=primary_color, markersize=8, markeredgecolor='white', markeredgewidth=2)
        
        # Customize the grid and axes
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels([])  # Hide radial labels
        ax.grid(True, color='#e0e0e0', linewidth=1, alpha=0.7)
        ax.set_facecolor('#f8f9fa')
        
        # Add metric labels
        ax.set_xticks(angles)
        ax.set_xticklabels(metrics, fontsize=11, fontweight='bold', color='#333333')
        
        # Add percentage labels on each point
        for angle, value, metric in zip(angles, values, metrics):
            # Better positioning logic for high percentile values
            if value >= 85:
                # For very high values, place label inside the chart
                label_distance = value - 15
                label_color = 'white'
                box_alpha = 0.9
            elif value >= 70:
                # For high values, place label slightly inside
                label_distance = value - 8
                label_color = 'white'
                box_alpha = 0.8
            else:
                # For lower values, place label outside
                label_distance = value + 12
                label_color = 'white'
                box_alpha = 0.8
                
            ax.annotate(f'{int(value)}', 
                       xy=(angle, label_distance), 
                       ha='center', va='center',
                       fontsize=10, fontweight='bold', 
                       color=label_color,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor=primary_color, alpha=box_alpha, edgecolor='none'))
        
        # Remove outer spines
        ax.spines['polar'].set_visible(False)
        
        # Add title and subtitle
        plt.figtext(0.5, 0.95, player_name, fontsize=22, fontweight='bold', ha='center', color='#2c3e50')
        max_rating = player_data.get('MAX', 'N/A')
        if max_rating != 'N/A':
            max_rating = round(float(max_rating))
        subtitle = f"Percentile rank vs. {position_desc} | {player_data.get('Minutes Played', 'N/A')} minutes | MAX Rating: {max_rating}"
        plt.figtext(0.5, 0.91, subtitle, fontsize=12, ha='center', color='#7f8c8d')
        
        # Add position-based legend
        legend_y = 0.08
        if position == 'Forward':
            legend_text = "● Attacking"
            legend_color = attacking_color
        elif position == 'Midfielder':
            legend_text = "● Possession"  
            legend_color = possession_color
        else:
            legend_text = "● Defending"
            legend_color = defending_color
            
        plt.figtext(0.5, legend_y, legend_text, fontsize=11, ha='center', color=legend_color, fontweight='600')
        
        # Adjust layout and save
        plt.tight_layout()
        plt.subplots_adjust(top=0.85, bottom=0.15)
        plt.savefig(filepath, dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close('all')  # Important: close all figures to free memory
        
        print(f"✓ Radar chart generated: {filename}")
        return filename
        
    except Exception as e:
        print(f"Error generating radar chart for {player_name}: {e}")
        plt.close('all')  # Close any open figures
        return None

def get_player_rating_data(player_name, generate_chart=True):
    """Get rating data for a specific player with optimized loading"""
    try:
        print(f"Loading rating data for {player_name}...")
        
        # Load and process data with minimal operations
        merged_df, _ = load_data()
        
        # Find the specific player first to avoid processing all data
        player_row = merged_df[merged_df['Name'] == player_name]
        if player_row.empty:
            print(f"Player {player_name} not found in data")
            return None
        
        # Only calculate stats for this player if found
        merged_df = calculate_per90_stats(merged_df)
        merged_df = normalize_stats(merged_df)
        merged_df = calculate_max_ratings(merged_df)
        merged_df = calculate_percentiles_by_position(merged_df)
        
        # Get the updated player data
        player_row = merged_df[merged_df['Name'] == player_name]
        player_data = player_row.iloc[0].to_dict()
        
        # Generate radar chart on demand with error protection
        if generate_chart:
            try:
                radar_filename = create_radar_chart(player_name, player_data)
                player_data['radar_chart'] = radar_filename
            except Exception as e:
                print(f"Error generating chart for {player_name}: {e}")
                player_data['radar_chart'] = None
        else:
            player_data['radar_chart'] = None
        
        return player_data
        
    except Exception as e:
        print(f"Error processing player {player_name}: {e}")
        return None

def get_team_max_ratings():
    """Calculate team MAX ratings using the original ncaaMatchPredictor method"""
    try:
        import sqlite3
        
        # Connect to database and get match data
        conn = sqlite3.connect('data/ncaa_soccer.db')
        
        # Get NCAA averages
        df = pd.read_sql_query("SELECT * FROM matches", conn)
        ncaa_avg_home_goals = df['home_team_score'].mean()
        ncaa_avg_away_goals = df['away_team_score'].mean()
        
        # Cap goal differences at maximum of 5 goals
        df['capped_home_team_score'] = df.apply(
            lambda row: min(row['home_team_score'], row['away_team_score'] + 5), axis=1
        )
        df['capped_away_team_score'] = df.apply(
            lambda row: min(row['away_team_score'], row['home_team_score'] + 5), axis=1
        )
        
        # Get unique teams and conferences (excluding non-D1)
        teams = df[df['home_team_conference'] != 'Not D1'][['home_team', 'home_team_conference']].drop_duplicates()
        home_df = teams.copy()
        home_df.columns = ['Team', 'Conference']
        
        # Calculate home stats using capped scores
        home_df['MP'] = home_df['Team'].apply(lambda team: len(df[df['home_team'] == team]))
        home_df['GF'] = home_df['Team'].apply(lambda team: df[df['home_team'] == team]['capped_home_team_score'].sum())
        home_df['GA'] = home_df['Team'].apply(lambda team: df[df['home_team'] == team]['capped_away_team_score'].sum())
        
        # Calculate conference averages for home games
        conf_home_avg = df[df['home_team_conference'] != 'Not D1'].groupby('home_team_conference')['capped_home_team_score'].mean()
        conf_away_avg_vs_home = df[df['home_team_conference'] != 'Not D1'].groupby('home_team_conference')['capped_away_team_score'].mean()
        
        home_df['ATT'] = home_df.apply(
            lambda row: ((row['GF'] / row['MP']) / ncaa_avg_home_goals) * 
                        (conf_home_avg[row['Conference']] / ncaa_avg_home_goals) if row['MP'] > 0 else 0,
            axis=1
        )
        
        home_df['DEF'] = home_df.apply(
            lambda row: ((row['GA'] / row['MP']) / ncaa_avg_away_goals) * 
                        (conf_away_avg_vs_home[row['Conference']] / ncaa_avg_away_goals) if row['MP'] > 0 else 0,
            axis=1
        )
        
        # Get away stats
        teams_away = df[df['away_team_conference'] != 'Not D1'][['away_team', 'away_team_conference']].drop_duplicates()
        away_df = teams_away.copy()
        away_df.columns = ['Team', 'Conference']
        
        away_df['MP'] = away_df['Team'].apply(lambda team: len(df[df['away_team'] == team]))
        away_df['GF'] = away_df['Team'].apply(lambda team: df[df['away_team'] == team]['capped_away_team_score'].sum())
        away_df['GA'] = away_df['Team'].apply(lambda team: df[df['away_team'] == team]['capped_home_team_score'].sum())
        
        # Calculate conference averages for away games
        conf_away_avg = df[df['away_team_conference'] != 'Not D1'].groupby('away_team_conference')['capped_away_team_score'].mean()
        conf_home_avg_vs_away = df[df['away_team_conference'] != 'Not D1'].groupby('away_team_conference')['capped_home_team_score'].mean()
        
        away_df['ATT'] = away_df.apply(
            lambda row: ((row['GF'] / row['MP']) / ncaa_avg_away_goals) * 
                        (conf_away_avg[row['Conference']] / ncaa_avg_away_goals) if row['MP'] > 0 else 0,
            axis=1
        )
        
        away_df['DEF'] = away_df.apply(
            lambda row: ((row['GA'] / row['MP']) / ncaa_avg_home_goals) * 
                        (conf_home_avg_vs_away[row['Conference']] / ncaa_avg_home_goals) if row['MP'] > 0 else 0,
            axis=1
        )
        
        # Merge home and away dataframes
        overall_df = pd.merge(home_df, away_df, on=['Team', 'Conference'], how='inner')
        
        # Combine metrics
        metrics = ['MP', 'GF', 'GA', 'ATT', 'DEF']
        for metric in metrics:
            overall_df[metric] = overall_df[f'{metric}_x'] + overall_df[f'{metric}_y']
        
        # Drop _x and _y columns
        columns_to_drop = [f'{metric}_x' for metric in metrics] + [f'{metric}_y' for metric in metrics]
        overall_df = overall_df.drop(columns=columns_to_drop)
        
        # Average ATT and DEF metrics
        overall_df['ATT'] = overall_df['ATT'] / 2
        overall_df['DEF'] = overall_df['DEF'] / 2
        
        # Calculate STR using linear defense scaling (Option 2)
        max_def = overall_df['DEF'].max()
        overall_df['STR'] = (overall_df['ATT'] * 0.5 + (max_def - overall_df['DEF']) * 0.5)
        overall_df['MAX'] = (overall_df['STR'] - overall_df['STR'].min()) / (overall_df['STR'].max() - overall_df['STR'].min()) * 100
        
        conn.close()
        return overall_df[['Team', 'ATT', 'DEF', 'MAX']].to_dict('records')
        
    except Exception as e:
        print(f"Error calculating team ratings: {e}")
        # Fallback to CSV file if calculation fails
        try:
            team_df = pd.read_csv('data/ncaa_ratings.csv')
            team_df = team_df.drop(columns=['Unnamed: 0'])
            return team_df[['Team', 'ATT', 'DEF', 'MAX']].to_dict('records')
        except:
            return []

if __name__ == "__main__":
    # Test the system
    test_player = "A.J. Schuetz"
    rating_data = get_player_rating_data(test_player)
    if rating_data:
        print(f"Successfully processed {test_player}")
        print(f"MAX Rating: {rating_data['MAX']}")
        print(f"Radar Chart: {rating_data['radar_chart']}")
    else:
        print(f"Failed to process {test_player}")
