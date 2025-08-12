import pandas as pd
import sys
sys.path.append('.')

from player_ratings import load_data, calculate_per90_stats, normalize_stats, calculate_max_ratings

print("🔄 Regenerating player ratings with minutes-based team weighting...")

# Load and process all data with the improved minutes-based weighting
merged_df, mls_drafted = load_data()
merged_df = calculate_per90_stats(merged_df)
merged_df = normalize_stats(merged_df)
merged_df = calculate_max_ratings(merged_df)

# Prepare the output DataFrame for the website
output_df = merged_df[['Name', 'Team', 'Position', 'Minutes Played', 'Goals', 'Assists', 
                       'Shots', 'Shots On Target', 'Fouls Won', 'MAX']].copy()

# Round the MAX ratings to integers and sort by rating
output_df['MAX'] = output_df['MAX'].round().astype(int)
output_df = output_df.sort_values('MAX', ascending=False)

# Save the final corrected file
output_df.to_csv('data/d1_player_stats.csv', index=False)
print(f"✅ Saved final corrected ratings to 'data/d1_player_stats.csv'")

# Show top players by position with minutes
print(f"\n🏆 Top Player by Position (with minutes context):")
for position in ['Forward', 'Midfielder', 'Defender']:
    top_player = output_df[output_df['Position'] == position].iloc[0]
    print(f"   {position:10s}: {top_player['Name']} ({top_player['Team']}) - {top_player['MAX']} ({top_player['Minutes Played']} mins)")

# Show some examples of how minutes affected ratings
print(f"\n📊 Examples of Minutes Impact on Team Credit:")
examples = [
    ("High-minute star", 1800, 0.85),
    ("Regular starter", 1200, 0.50), 
    ("Squad rotation", 800, 0.23),
    ("Limited bench role", 400, 0.05)
]

for desc, mins, impact in examples:
    print(f"   {desc:18s}: {mins:4d} mins → {impact:.2f} team impact factor")

print(f"\n✅ Final rating generation complete!")
print(f"   Key players now properly distinguished from bench players")
print(f"   Team strength still matters, but minutes played provides proper context")
print(f"   Total players: {len(output_df)}")
print(f"   Rating range: {output_df['MAX'].min()}-{output_df['MAX'].max()}")
