import pandas as pd
import sys
sys.path.append('.')

# Import rating calculation functions 
from player_ratings import load_data, calculate_per90_stats, normalize_stats

def calculate_max_ratings_fixed(df):
    """Calculate MAX ratings with the fixed DEF normalization"""
    
    # Position-based weights (from the original code)
    weights = {
        'Forward': {
            'Goals': 0.312,
            'Assists': 0.126,
            'Shots': 0.211,
            'Fouls_Won': 0.127,
            'Team_Att': 0.224
        },
        'Midfielder': {
            'Goals': 0.145,
            'Assists': 0.210,
            'Shots': 0.158,
            'Fouls_Won': 0.147,
            'Team_Att_Def': 0.340
        },
        'Defender': {
            'Goals': 0.002,
            'Assists': 0.048,
            'Shots': 0.076,
            'Fouls_Won': 0.120,
            'Team_Def': 0.754
        },
        'Unknown': {
            'Goals': 0.200,
            'Assists': 0.150,
            'Shots': 0.150,
            'Fouls_Won': 0.150,
            'Team_Att_Def': 0.350
        }
    }
    
    def calculate_rating(row):
        position = row['Position']
        
        if position == 'Forward':
            return 100 * (
                row['Norm_Goals'] * weights['Forward']['Goals'] +
                row['Norm_Assists'] * weights['Forward']['Assists'] +
                row['Norm_Shots'] * weights['Forward']['Shots'] +
                row['Norm_Fouls_Won'] * weights['Forward']['Fouls_Won'] +
                row['Norm_ATT'] * row['Team_Minutes_Played_Percentage'] * weights['Forward']['Team_Att']
            )
        elif position == 'Midfielder':
            return 100 * (
                row['Norm_Goals'] * weights['Midfielder']['Goals'] +
                row['Norm_Assists'] * weights['Midfielder']['Assists'] +
                row['Norm_Shots'] * weights['Midfielder']['Shots'] +
                row['Norm_Fouls_Won'] * weights['Midfielder']['Fouls_Won'] +
                ((row['Norm_ATT'] + row['Norm_DEF']) / 2) * row['Team_Minutes_Played_Percentage'] * weights['Midfielder']['Team_Att_Def']
            )
        elif position == 'Defender':
            return 100 * (
                row['Norm_Goals'] * weights['Defender']['Goals'] +
                row['Norm_Assists'] * weights['Defender']['Assists'] +
                row['Norm_Shots'] * weights['Defender']['Shots'] +
                row['Norm_Fouls_Won'] * weights['Defender']['Fouls_Won'] +
                row['Norm_DEF'] * row['Team_Minutes_Played_Percentage'] * weights['Defender']['Team_Def']
            )
        else:  # Unknown position
            return 100 * (
                row['Norm_Goals'] * weights['Unknown']['Goals'] +
                row['Norm_Assists'] * weights['Unknown']['Assists'] +
                row['Norm_Shots'] * weights['Unknown']['Shots'] +
                row['Norm_Fouls_Won'] * weights['Unknown']['Fouls_Won'] +
                ((row['Norm_ATT'] + row['Norm_DEF']) / 2) * row['Team_Minutes_Played_Percentage'] * weights['Unknown']['Team_Att_Def']
            )
    
    df['MAX_Fixed'] = df.apply(calculate_rating, axis=1)
    return df

# Load and process data
merged_df, mls_drafted = load_data()
merged_df = calculate_per90_stats(merged_df)
merged_df = normalize_stats(merged_df)
merged_df = calculate_max_ratings_fixed(merged_df)

# Check Elijah Jackson's new rating
elijah = merged_df[merged_df['Name'] == 'Elijah Jackson']
if not elijah.empty:
    print("🎯 Elijah Jackson's Rating After Fix:")
    print(f"Name: {elijah['Name'].iloc[0]}")
    print(f"Team: {elijah['Team'].iloc[0]}")
    print(f"Position: {elijah['Position'].iloc[0]}")
    print(f"DEF Rating: {elijah['DEF'].iloc[0]:.3f} (worst defense)")
    print(f"Norm_DEF: {elijah['Norm_DEF'].iloc[0]:.3f}")
    print(f"Fouls Won per 90: {elijah['Fouls Won_per90'].iloc[0]:.2f}")
    print(f"NEW MAX Rating: {elijah['MAX_Fixed'].iloc[0]:.1f}")
    print()

# Show top 10 defenders after the fix
print("🏆 Top 10 Defenders After Fix:")
defenders = merged_df[merged_df['Position'] == 'Defender'].nlargest(10, 'MAX_Fixed')
for i, (_, defender) in enumerate(defenders.iterrows(), 1):
    print(f"{i:2d}. {defender['Name']:20s} ({defender['Team']:15s}) - {defender['MAX_Fixed']:5.1f} (DEF: {defender['DEF']:.2f})")

print("\n🏆 Bottom 10 Defenders After Fix:")
bottom_defenders = merged_df[merged_df['Position'] == 'Defender'].nsmallest(10, 'MAX_Fixed')
for i, (_, defender) in enumerate(bottom_defenders.iterrows(), 1):
    print(f"{i:2d}. {defender['Name']:20s} ({defender['Team']:15s}) - {defender['MAX_Fixed']:5.1f} (DEF: {defender['DEF']:.2f})")
