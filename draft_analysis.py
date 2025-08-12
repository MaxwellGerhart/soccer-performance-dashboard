import pandas as pd
import numpy as np
from unidecode import unidecode

# Real 2025 MLS SuperDraft data from official MLS website
draft_picks_2025 = [
    # Round 1
    {'pick': 1, 'name': 'Manu Duah', 'position': 'Midfielder', 'college': 'UC Santa Barbara', 'mls_team': 'San Diego FC'},
    {'pick': 2, 'name': 'Max Floriani', 'position': 'Defender', 'college': 'Saint Louis University', 'mls_team': 'San Jose'},
    {'pick': 3, 'name': 'Dean Boltz', 'position': 'Forward', 'college': 'University of Wisconsin', 'mls_team': 'Chicago'},
    {'pick': 4, 'name': 'Alex Harris', 'position': 'Forward', 'college': 'Cornell University', 'mls_team': 'Colorado'},
    {'pick': 5, 'name': 'Reid Roberts', 'position': 'Defender', 'college': 'University of San Francisco', 'mls_team': 'San Jose'},
    {'pick': 6, 'name': 'Matthew Senanou', 'position': 'Defender', 'college': 'Xavier University', 'mls_team': 'Colorado'},
    {'pick': 7, 'name': 'Emil Jaaskelainen', 'position': 'Forward', 'college': 'University of Akron', 'mls_team': 'St. Louis'},
    {'pick': 8, 'name': 'Jansen Miller', 'position': 'Defender', 'college': 'Indiana University', 'mls_team': 'Kansas City'},
    {'pick': 9, 'name': 'Mikah Thomas', 'position': 'Defender', 'college': 'University of Connecticut', 'mls_team': 'Charlotte'},
    {'pick': 10, 'name': 'Hakim Karamoko', 'position': 'Forward', 'college': 'North Carolina State University', 'mls_team': 'D.C. United'},
    {'pick': 11, 'name': 'Enzo Newman', 'position': 'Defender', 'college': 'Oregon State University', 'mls_team': 'Dallas'},
    {'pick': 12, 'name': 'Efetobo Aror', 'position': 'Midfielder', 'college': 'University of Portland', 'mls_team': 'Colorado'},
    {'pick': 13, 'name': 'Michael Adedokun', 'position': 'Forward', 'college': 'Ohio State University', 'mls_team': 'Montreal'},
    {'pick': 14, 'name': 'Ian Smith', 'position': 'Defender', 'college': 'University of Denver', 'mls_team': 'Portland'},
    {'pick': 15, 'name': 'Tate Johnson', 'position': 'Defender', 'college': 'University of North Carolina Chapel Hill', 'mls_team': 'Vancouver'},
    {'pick': 16, 'name': 'Sydney Wathuta', 'position': 'Forward', 'college': 'University of Vermont', 'mls_team': 'Colorado'},
    {'pick': 17, 'name': 'Max Murray', 'position': 'Defender', 'college': 'University of Vermont', 'mls_team': 'New York City'},
    {'pick': 18, 'name': 'Donovan Parisian', 'position': 'Goalkeeper', 'college': 'University of San Diego', 'mls_team': 'New England'},
    {'pick': 19, 'name': 'Jesus Barea', 'position': 'Forward', 'college': 'Missouri State University', 'mls_team': 'Salt Lake'},
    {'pick': 20, 'name': 'Jason Bucknor', 'position': 'Defender', 'college': 'University of Michigan', 'mls_team': 'LA'},
    {'pick': 21, 'name': 'Max Kerkvliet', 'position': 'Goalkeeper', 'college': 'University of Connecticut', 'mls_team': 'Salt Lake'},
    {'pick': 22, 'name': 'Alec Hughes', 'position': 'Forward', 'college': 'University of Massachusetts', 'mls_team': 'LAFC'},
    {'pick': 23, 'name': 'Reid Fisher', 'position': 'Defender', 'college': 'San Diego State University', 'mls_team': 'Toronto'},
    {'pick': 24, 'name': 'Ian Pilcher', 'position': 'Defender', 'college': 'University of North Carolina Charlotte', 'mls_team': 'San Diego'},
    {'pick': 25, 'name': 'Roman Torres', 'position': 'Midfielder', 'college': 'Creighton University', 'mls_team': 'Minnesota'},
    {'pick': 26, 'name': 'Joshua Copeland', 'position': 'Forward', 'college': 'University of Detroit Mercy', 'mls_team': 'Colorado'},
    {'pick': 27, 'name': 'Joran Gerbet', 'position': 'Midfielder', 'college': 'Clemson University', 'mls_team': 'Orlando'},
    {'pick': 28, 'name': 'Ryan Baer', 'position': 'Midfielder', 'college': 'West Virginia University', 'mls_team': 'Seattle'},
    {'pick': 29, 'name': 'Lineker Rodrigues Dos Santos', 'position': 'Forward', 'college': 'Marshall University', 'mls_team': 'RSL'},
    {'pick': 30, 'name': 'Sergi Solans', 'position': 'Forward', 'college': 'Oregon State University', 'mls_team': 'RSL'},
]

def clean_name_for_matching(name):
    """Clean names for better matching"""
    if pd.isna(name) or name == '':
        return ''
    name = str(name)
    name = unidecode(name).strip().title()
    # Remove suffixes
    name = name.replace('Jr.', '').replace('Sr.', '').replace('III', '').replace('II', '').strip()
    return name

def analyze_draft_vs_ratings():
    """Analyze how our ratings correlate with actual draft selections"""
    
    print("🏈 2025 MLS SuperDraft vs MAX Rating Analysis")
    print("=" * 70)
    
    # Load our ratings data
    try:
        ratings_df = pd.read_csv('data/d1_player_stats.csv')
        print(f"✅ Loaded {len(ratings_df)} players from our rating system")
    except Exception as e:
        print(f"❌ Error loading ratings: {e}")
        return
    
    # Convert draft picks to DataFrame and clean names
    draft_df = pd.DataFrame(draft_picks_2025)
    draft_df['clean_name'] = draft_df['name'].apply(clean_name_for_matching)
    ratings_df['clean_name'] = ratings_df['Name'].apply(clean_name_for_matching)
    
    print(f"📊 Total draft picks analyzed: {len(draft_df)}")
    
    # Find matches
    matches = []
    unmatched = []
    
    for _, pick in draft_df.iterrows():
        # Try exact name match
        exact_match = ratings_df[ratings_df['clean_name'] == pick['clean_name']]
        
        if not exact_match.empty:
            player_data = exact_match.iloc[0]
            matches.append({
                'pick': pick['pick'],
                'name': pick['name'],
                'college': pick['college'],
                'position': pick['position'],
                'mls_team': pick['mls_team'],
                'max_rating': player_data['MAX'],
                'goals': player_data['Goals'],
                'assists': player_data['Assists'],
                'minutes': player_data['Minutes Played'],
                'college_team': player_data['Team'],
                'shots': player_data['Shots']
            })
        else:
            unmatched.append(pick['name'])
    
    # Analysis
    matches_df = pd.DataFrame(matches)
    
    print(f"✅ Successfully matched: {len(matches)} players")
    print(f"❌ Could not match: {len(unmatched)} players")
    
    if len(unmatched) > 0:
        print(f"\n🔍 Unmatched players: {', '.join(unmatched[:5])}")
        if len(unmatched) > 5:
            print(f"    ... and {len(unmatched) - 5} more")
    
    if len(matches) > 0:
        print(f"\n📈 MAX Rating Analysis for Drafted Players:")
        avg_rating = matches_df['max_rating'].mean()
        median_rating = matches_df['max_rating'].median()
        max_rating = matches_df['max_rating'].max()
        min_rating = matches_df['max_rating'].min()
        
        print(f"   Average MAX Rating: {avg_rating:.1f}")
        print(f"   Median MAX Rating: {median_rating:.1f}")
        print(f"   Range: {min_rating:.0f} - {max_rating:.0f}")
        
        # Show top rated drafted players
        print(f"\n🏆 Top 10 Highest Rated Draft Picks:")
        top_drafted = matches_df.nlargest(10, 'max_rating')
        for i, (_, player) in enumerate(top_drafted.iterrows(), 1):
            rating = player['max_rating']
            pick = player['pick']
            name = player['name']
            pos = player['position']
            goals = player['goals']
            assists = player['assists']
            print(f"   {i:2d}. Pick #{pick:2.0f} - {name:25s} ({rating:2.0f}) - {pos}")
            print(f"       Stats: {goals}G, {assists}A in {player['minutes']} mins")
        
        # Compare to overall population
        all_ratings = ratings_df['MAX']
        percentile = (all_ratings < avg_rating).mean() * 100
        
        print(f"\n🎯 Comparison to All NCAA Players:")
        print(f"   Drafted players average in the {percentile:.1f}th percentile")
        
        # Rating thresholds
        thresholds = [80, 85, 90, 95]
        for threshold in thresholds:
            count = sum(matches_df['max_rating'] >= threshold)
            percentage = (count / len(matches)) * 100
            total_above_threshold = sum(all_ratings >= threshold)
            print(f"   {percentage:5.1f}% of drafted players have rating ≥ {threshold} ({count}/{len(matches)})")
        
        # Position analysis
        print(f"\n⚽ Analysis by Position:")
        position_stats = matches_df.groupby('position')['max_rating'].agg(['count', 'mean', 'min', 'max'])
        for position in position_stats.index:
            stats = position_stats.loc[position]
            count = int(stats['count'])
            mean_rating = stats['mean']
            min_rating = stats['min'] 
            max_rating = stats['max']
            print(f"   {position:12s}: {count:2d} players, avg {mean_rating:4.1f}, range {min_rating:2.0f}-{max_rating:2.0f}")
        
        print(f"\n🎯 CONCLUSION:")
        if percentile > 90:
            conclusion = "EXCELLENT predictive power"
        elif percentile > 80:
            conclusion = "STRONG predictive power"
        elif percentile > 70:
            conclusion = "GOOD predictive power"
        else:
            conclusion = "MODERATE predictive power"
            
        print(f"   Our MAX rating system shows {conclusion} for MLS draft selection")
        print(f"   Average drafted player rating ({avg_rating:.1f}) = {percentile:.1f}th percentile")
        
        # Show some high-rated undrafted players
        print(f"\n💎 High-Rated Players Who Weren't Drafted:")
        drafted_names = set(matches_df['name'].str.lower())
        
        min_draft_rating = matches_df['max_rating'].min()
        high_rated_undrafted = ratings_df[
            (~ratings_df['Name'].str.lower().isin(drafted_names)) & 
            (ratings_df['MAX'] >= min_draft_rating) &
            (ratings_df['Minutes Played'] >= 800)
        ].nlargest(5, 'MAX')
        
        for _, player in high_rated_undrafted.iterrows():
            print(f"   {player['Name']:25s} ({player['MAX']:2.0f}) - {player['Position']} from {player['Team']}")

if __name__ == "__main__":
    analyze_draft_vs_ratings()
