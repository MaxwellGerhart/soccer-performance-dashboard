import pandas as pd
import sys
sys.path.append('.')

from player_ratings import get_position_weights

weights = get_position_weights()

print("🏃‍♂️ Current Midfielder Weights:")
print("="*40)
for stat, weight in weights['Midfielder'].items():
    print(f"{stat:15s}: {weight:.3f} ({weight*100:.1f}%)")

print(f"\nTotal: {sum(weights['Midfielder'].values()):.3f}")

print("\n📊 Midfielder Rating Breakdown:")
print("- Individual performance: Goals + Assists + Shots + Fouls Won")
print(f"  = {weights['Midfielder']['Goals']*100:.1f}% + {weights['Midfielder']['Assists']*100:.1f}% + {weights['Midfielder']['Shots']*100:.1f}% + {weights['Midfielder']['Fouls_Won']*100:.1f}% = {(weights['Midfielder']['Goals'] + weights['Midfielder']['Assists'] + weights['Midfielder']['Shots'] + weights['Midfielder']['Fouls_Won'])*100:.1f}%")
print(f"- Team performance (ATT+DEF average): {weights['Midfielder']['Team_Att_Def']*100:.1f}%")

print("\n🔧 Impact of DEF Fix on Midfielders:")
print("- Midfielders use AVERAGE of Norm_ATT and Norm_DEF")
print("- Since Norm_DEF is now properly inverted:")
print("  * Players on good defensive teams get higher Norm_DEF values")
print("  * Players on bad defensive teams get lower Norm_DEF values")
print("  * The (ATT + DEF)/2 average is now more accurate")
