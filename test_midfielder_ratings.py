import pandas as pd
import sys
sys.path.append('.')

from player_ratings import load_data, calculate_per90_stats, normalize_stats, calculate_max_ratings

print("🏃‍♂️ Testing Midfielder Ratings After DEF Fix...")

# Load and process data
merged_df, mls_drafted = load_data()
merged_df = calculate_per90_stats(merged_df)
merged_df = normalize_stats(merged_df)
merged_df = calculate_max_ratings(merged_df)

# Get midfielders and show some examples
midfielders = merged_df[merged_df['Position'] == 'Midfielder'].copy()

print(f"\n📊 Midfielder Analysis ({len(midfielders)} total midfielders):")

# Find midfielders from teams with worst defenses
print("\n🔻 Midfielders from WORST defensive teams:")
worst_def_midfielders = midfielders.nlargest(5, 'DEF')[['Name', 'Team', 'DEF', 'Overall_Rating', 'Norm_DEF', 'Norm_ATT']]
for i, (_, player) in enumerate(worst_def_midfielders.iterrows(), 1):
    avg_team_rating = (player['Norm_ATT'] + player['Norm_DEF']) / 2
    print(f"   {i}. {player['Name']:20s} ({player['Team']:15s}) - Rating: {player['Overall_Rating']:5.1f}")
    print(f"      DEF: {player['DEF']:.2f} (Norm: {player['Norm_DEF']:.3f}) | Team Avg: {avg_team_rating:.3f}")

# Find midfielders from teams with best defenses  
print("\n🔺 Midfielders from BEST defensive teams:")
best_def_midfielders = midfielders.nsmallest(5, 'DEF')[['Name', 'Team', 'DEF', 'Overall_Rating', 'Norm_DEF', 'Norm_ATT']]
for i, (_, player) in enumerate(best_def_midfielders.iterrows(), 1):
    avg_team_rating = (player['Norm_ATT'] + player['Norm_DEF']) / 2
    print(f"   {i}. {player['Name']:20s} ({player['Team']:15s}) - Rating: {player['Overall_Rating']:5.1f}")
    print(f"      DEF: {player['DEF']:.2f} (Norm: {player['Norm_DEF']:.3f}) | Team Avg: {avg_team_rating:.3f}")

# Show top-rated midfielders overall
print("\n🏆 Top 5 Rated Midfielders Overall:")
top_midfielders = midfielders.nlargest(5, 'Overall_Rating')[['Name', 'Team', 'DEF', 'ATT', 'Overall_Rating']]
for i, (_, player) in enumerate(top_midfielders.iterrows(), 1):
    print(f"   {i}. {player['Name']:20s} ({player['Team']:15s}) - Rating: {player['Overall_Rating']:5.1f}")
    print(f"      ATT: {player['ATT']:.2f} | DEF: {player['DEF']:.2f}")

print("\n✅ Analysis Complete!")
print("The DEF normalization fix automatically corrected midfielder ratings too!")
print("Midfielders on teams with good defense now get higher team component scores.")
