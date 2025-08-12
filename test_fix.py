import pandas as pd
import sys
sys.path.append('.')

from player_ratings import load_data, calculate_per90_stats, normalize_stats

# Load and process data
merged_df, mls_drafted = load_data()
merged_df = calculate_per90_stats(merged_df)
merged_df = normalize_stats(merged_df)

# Check USC Upstate's normalized DEF rating after fix
usc_upstate = merged_df[merged_df['Team'] == 'USC Upstate']
if not usc_upstate.empty:
    print("USC Upstate after fix:")
    print(f"DEF Rating: {usc_upstate['DEF'].iloc[0]:.3f}")
    print(f"Norm_DEF: {usc_upstate['Norm_DEF'].iloc[0]:.3f}")
    print("(Should be close to 0 since they have the worst defense)")

# Check Cal Poly (best defense)
cal_poly = merged_df[merged_df['Team'] == 'Cal Poly']
if not cal_poly.empty:
    print("\nCal Poly after fix:")
    print(f"DEF Rating: {cal_poly['DEF'].iloc[0]:.3f}")
    print(f"Norm_DEF: {cal_poly['Norm_DEF'].iloc[0]:.3f}")
    print("(Should be close to 1.0 since they have the best defense)")

# Check Elijah Jackson specifically
elijah = merged_df[merged_df['Name'] == 'Elijah Jackson']
if not elijah.empty:
    print(f"\nElijah Jackson:")
    print(f"Team: {elijah['Team'].iloc[0]}")
    print(f"DEF Rating: {elijah['DEF'].iloc[0]:.3f}")
    print(f"Norm_DEF: {elijah['Norm_DEF'].iloc[0]:.3f}")
    print(f"Fouls Won per 90: {elijah['Fouls Won_per90'].iloc[0]:.2f}")
    print(f"Norm_Fouls_Won: {elijah['Norm_Fouls_Won'].iloc[0]:.3f}")
else:
    print("Elijah Jackson not found")

print(f"\nDEF normalization range:")
print(f"Min Norm_DEF: {merged_df['Norm_DEF'].min():.3f}")
print(f"Max Norm_DEF: {merged_df['Norm_DEF'].max():.3f}")
