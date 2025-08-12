import pandas as pd
import numpy as np
import sys
sys.path.append('.')

from player_ratings import load_data, calculate_per90_stats, normalize_stats, get_position_weights

# Load the data to debug
merged_df, mls_drafted = load_data()
merged_df = calculate_per90_stats(merged_df)

print("🔍 Debugging Forward Rating Issues...")
print("="*50)

# Check some top forwards before normalization
print("\n📊 Sample Forward Stats Before Normalization:")
forwards = merged_df[merged_df['Position'] == 'Forward'].copy()
top_scorers = forwards.nlargest(3, 'Goals_per90')
for i, (_, player) in enumerate(top_scorers.iterrows(), 1):
    print(f"{i}. {player['Name']} ({player['Team']})")
    print(f"   Goals/90: {player['Goals_per90']:.3f}")
    print(f"   Assists/90: {player['Assists_per90']:.3f}")
    print(f"   Shots/90: {player['Shots_per90']:.3f}")
    print(f"   ATT: {player['ATT']:.3f}")

# Apply normalization
merged_df = normalize_stats(merged_df)

print("\n📊 After Normalization:")
for i, (_, player) in enumerate(top_scorers.iterrows(), 1):
    idx = merged_df[merged_df['Name'] == player['Name']].index[0]
    norm_player = merged_df.loc[idx]
    print(f"{i}. {player['Name']} ({player['Team']})")
    print(f"   Norm_Goals: {norm_player['Norm_Goals']:.3f}")
    print(f"   Norm_Assists: {norm_player['Norm_Assists']:.3f}")
    print(f"   Norm_Shots: {norm_player['Norm_Shots']:.3f}")
    print(f"   Norm_ATT: {norm_player['Norm_ATT']:.3f}")

# Check forward weights
weights = get_position_weights()
print(f"\n⚖️  Forward Weights:")
for stat, weight in weights['Forward'].items():
    print(f"   {stat}: {weight:.3f} ({weight*100:.1f}%)")

# Calculate a sample forward rating manually
sample_player = merged_df[merged_df['Name'] == top_scorers.iloc[0]['Name']].iloc[0]
rating = (
    sample_player['Norm_Goals'] * weights['Forward']['Goals'] +
    sample_player['Norm_Assists'] * weights['Forward']['Assists'] +
    sample_player['Norm_Shots'] * weights['Forward']['Shots'] +
    sample_player['Norm_Fouls_Won'] * weights['Forward']['Fouls_Won'] +
    sample_player['Norm_ATT'] * sample_player['Team_Minutes_Played_Percentage'] * weights['Forward']['Team_Att']
) * 100

print(f"\n🧮 Manual Rating Calculation for {sample_player['Name']}:")
print(f"   Raw Overall Rating: {rating:.1f}")
print(f"   Team Minutes %: {sample_player['Team_Minutes_Played_Percentage']:.3f}")

print(f"\n🔍 Checking ranges for Forward stats:")
print(f"   Goals/90 range: {forwards['Goals_per90'].min():.3f} to {forwards['Goals_per90'].max():.3f}")
print(f"   Assists/90 range: {forwards['Assists_per90'].min():.3f} to {forwards['Assists_per90'].max():.3f}")
print(f"   ATT range: {forwards['ATT'].min():.3f} to {forwards['ATT'].max():.3f}")
