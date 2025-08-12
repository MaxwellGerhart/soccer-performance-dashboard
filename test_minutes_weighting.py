import pandas as pd
import numpy as np
import sys
sys.path.append('.')

from player_ratings import load_data, calculate_per90_stats, normalize_stats, calculate_max_ratings

print("🔧 Testing Improved Team Impact Factor...")

# Load and process data with the improved weighting
merged_df, mls_drafted = load_data()
merged_df = calculate_per90_stats(merged_df)
merged_df = normalize_stats(merged_df)
merged_df = calculate_max_ratings(merged_df)

# Check Ohio State midfielders specifically
print("\n🏈 Ohio State Midfielders After Minutes-Based Weighting:")
ohio_mids = merged_df[(merged_df['Team'] == 'Ohio St.') & (merged_df['Position'] == 'Midfielder')].copy()
ohio_mids = ohio_mids.sort_values('MAX', ascending=False)

for i, (_, player) in enumerate(ohio_mids.iterrows(), 1):
    impact_factor = player['Team_Impact_Factor']
    minutes = int(player['Minutes Played'])
    rating = int(player['MAX'])
    
    # Classify playing time
    if minutes >= 1500:
        status = "Key Player"
    elif minutes >= 1000:
        status = "Regular"
    elif minutes >= 600:
        status = "Squad Player"
    else:
        status = "Limited Role"
    
    print(f"{i:2d}. {player['Name']:20s} - {rating:2d} ({minutes:4d} mins, Impact: {impact_factor:.3f}, {status})")

# Check top midfielders overall
print("\n🏆 Top 10 Midfielders After Minutes-Based Fix:")
top_mids = merged_df[merged_df['Position'] == 'Midfielder'].nlargest(10, 'MAX')
for i, (_, player) in enumerate(top_mids.iterrows(), 1):
    minutes = int(player['Minutes Played'])
    rating = int(player['MAX'])
    impact = player['Team_Impact_Factor']
    print(f"{i:2d}. {player['Name']:20s} ({player['Team']:15s}) - {rating:2d} ({minutes:4d} mins, {impact:.3f})")

# Show the impact factor curve
print(f"\n📊 Team Impact Factor Examples:")
sample_minutes = [300, 500, 800, 1200, 1500, 1800, 2000]
for mins in sample_minutes:
    # Calculate the impact factor manually
    base_impact = 1 / (1 + np.exp(-0.003 * (mins - 1200)))
    if mins < 600:
        base_impact *= 0.6
    if mins < 400:
        base_impact *= 0.5
    
    print(f"   {mins:4d} minutes: Impact Factor = {base_impact:.3f}")

print(f"\n✅ Minutes-based weighting should now properly differentiate key players from bench players!")
