import pandas as pd
import sys
sys.path.append('.')

from player_ratings import load_data, calculate_per90_stats, normalize_stats, calculate_max_ratings

print("🔄 Regenerating corrected player ratings...")

# Load and process all data with the fix
merged_df, mls_drafted = load_data()
merged_df = calculate_per90_stats(merged_df)
merged_df = normalize_stats(merged_df)
merged_df = calculate_max_ratings(merged_df)

# Prepare the output DataFrame in the format the website expects
# The website probably expects the same columns as the original d1_player_stats.csv
output_df = merged_df[['Name', 'Team', 'Position', 'Minutes Played', 'Goals', 'Assists', 
                       'Shots', 'Shots On Target', 'Fouls Won', 'MAX']].copy()

# Round the MAX ratings to integers for consistency
output_df['MAX'] = output_df['MAX'].round().astype(int)

# Sort by MAX rating descending so the website displays correctly
output_df = output_df.sort_values('MAX', ascending=False)

# Save the corrected file
output_df.to_csv('data/d1_player_stats.csv', index=False)
print(f"✅ Saved corrected ratings to 'data/d1_player_stats.csv'")

# Also save the full data with team ratings for analysis
full_output = merged_df[['Name', 'Team', 'Position', 'Minutes Played', 'Goals', 'Assists', 
                         'Shots', 'Shots On Target', 'Fouls Won', 'Conference', 'ATT', 'DEF', 'MAX']].copy()
full_output['MAX'] = full_output['MAX'].round().astype(int)
full_output = full_output.sort_values('MAX', ascending=False)
full_output.to_csv('data/d1_player_stats_updated.csv', index=False)

print(f"✅ Also saved full data to 'data/d1_player_stats_updated.csv'")
print(f"   Total players: {len(output_df)}")

# Show top players by position
print(f"\n🏆 Top Players by Position:")
for position in ['Forward', 'Midfielder', 'Defender']:
    top_player = output_df[output_df['Position'] == position].iloc[0]
    print(f"   {position:10s}: {top_player['Name']} ({top_player['Team']}) - {top_player['MAX']}")

print(f"\n✅ Rating regeneration complete! Sorting should now work correctly.")
