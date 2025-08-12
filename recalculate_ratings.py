import pandas as pd
import sys
sys.path.append('.')

from player_ratings import load_data, calculate_per90_stats, normalize_stats, calculate_max_ratings

print("🔄 Recalculating all player ratings with fixed DEF normalization...")

# Load and process all data
merged_df, mls_drafted = load_data()
print(f"✅ Loaded {len(merged_df)} players")

# Calculate ratings
merged_df = calculate_per90_stats(merged_df)
merged_df = normalize_stats(merged_df)  
merged_df = calculate_max_ratings(merged_df)
print("✅ Calculated ratings for all players")

# Check Elijah Jackson
elijah = merged_df[merged_df['Name'] == 'Elijah Jackson']
if not elijah.empty:
    print(f"\n🎯 Elijah Jackson's Fixed Rating:")
    print(f"   Name: {elijah['Name'].iloc[0]}")
    print(f"   Team: {elijah['Team'].iloc[0]} (DEF: {elijah['DEF'].iloc[0]:.2f})")
    print(f"   MAX Rating: {elijah['MAX'].iloc[0]:.1f}")
else:
    print("❌ Elijah Jackson not found")

# Show top 5 defenders
print(f"\n🏆 Top 5 Defenders After Fix:")
top_defenders = merged_df[merged_df['Position'] == 'Defender'].nlargest(5, 'MAX')
for i, (_, defender) in enumerate(top_defenders.iterrows(), 1):
    print(f"   {i}. {defender['Name']} ({defender['Team']}) - {defender['MAX']:.1f} (DEF: {defender['DEF']:.2f})")

# Show USC Upstate defenders specifically
print(f"\n🔍 USC Upstate Defenders (should all be low-rated now):")
usc_defenders = merged_df[(merged_df['Team'] == 'USC Upstate') & (merged_df['Position'] == 'Defender')].sort_values('MAX', ascending=False)
for i, (_, defender) in enumerate(usc_defenders.iterrows(), 1):
    print(f"   {i}. {defender['Name']} - {defender['MAX']:.1f}")

# Save updated data to CSV for the website to use
output_df = merged_df[['Name', 'Team', 'Position', 'Minutes Played', 'Goals', 'Assists', 
                       'Shots', 'Shots On Target', 'Fouls Won', 'Conference', 'ATT', 'DEF', 'MAX']]
output_df.to_csv('data/d1_player_stats_updated.csv', index=False)
print(f"\n💾 Saved updated ratings to 'data/d1_player_stats_updated.csv'")
print(f"   Total players: {len(output_df)}")

print("\n✅ Fix complete! The defensive rating normalization has been corrected.")
print("   Players on bad defensive teams now get appropriately lower ratings.")
print("   Players on good defensive teams get higher ratings as expected.")
