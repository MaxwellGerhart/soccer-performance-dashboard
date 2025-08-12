import pandas as pd
import numpy as np
import sys
sys.path.append('.')

from player_ratings import load_data, calculate_per90_stats, normalize_stats, calculate_max_ratings

print("🔧 Testing Fixed Rating Calculation...")

# Load and process data
merged_df, mls_drafted = load_data()
merged_df = calculate_per90_stats(merged_df)
merged_df = normalize_stats(merged_df)
merged_df = calculate_max_ratings(merged_df)

# Check top forwards
print("\n🏆 Top 10 Forwards After Fix:")
top_forwards = merged_df[merged_df['Position'] == 'Forward'].nlargest(10, 'MAX')
for i, (_, player) in enumerate(top_forwards.iterrows(), 1):
    print(f"{i:2d}. {player['Name']:25s} ({player['Team']:15s}) - {int(player['MAX']):3d} (ATT: {player['ATT']:.2f})")

print("\n🏆 Top 10 Defenders After Fix:")
top_defenders = merged_df[merged_df['Position'] == 'Defender'].nlargest(10, 'MAX')
for i, (_, player) in enumerate(top_defenders.iterrows(), 1):
    print(f"{i:2d}. {player['Name']:25s} ({player['Team']:15s}) - {int(player['MAX']):3d} (DEF: {player['DEF']:.2f})")

print("\n🏆 Top 10 Midfielders After Fix:")
top_midfielders = merged_df[merged_df['Position'] == 'Midfielder'].nlargest(10, 'MAX')
for i, (_, player) in enumerate(top_midfielders.iterrows(), 1):
    print(f"{i:2d}. {player['Name']:25s} ({player['Team']:15s}) - {int(player['MAX']):3d} (ATT: {player['ATT']:.2f}, DEF: {player['DEF']:.2f})")

# Check Elijah Jackson specifically  
elijah = merged_df[merged_df['Name'] == 'Elijah Jackson']
if not elijah.empty:
    print(f"\n🎯 Elijah Jackson (USC Upstate) After Fix:")
    print(f"   Rating: {int(elijah['MAX'].iloc[0]):3d}")
    print(f"   DEF: {elijah['DEF'].iloc[0]:.2f}")
    print(f"   Team Impact Factor: {elijah['Team_Impact_Factor'].iloc[0]:.3f}")

print(f"\n📊 Rating Distribution:")
print(f"   Forward ratings: {merged_df[merged_df['Position'] == 'Forward']['MAX'].min()}-{merged_df[merged_df['Position'] == 'Forward']['MAX'].max()}")
print(f"   Midfielder ratings: {merged_df[merged_df['Position'] == 'Midfielder']['MAX'].min()}-{merged_df[merged_df['Position'] == 'Midfielder']['MAX'].max()}")
print(f"   Defender ratings: {merged_df[merged_df['Position'] == 'Defender']['MAX'].min()}-{merged_df[merged_df['Position'] == 'Defender']['MAX'].max()}")
