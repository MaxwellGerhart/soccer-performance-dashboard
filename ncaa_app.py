from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
from urllib.parse import unquote
import math

# Try to import player ratings - handle gracefully if it fails
try:
    from player_ratings import get_player_rating_data, get_team_max_ratings
    RATINGS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Player ratings module not available: {e}")
    RATINGS_AVAILABLE = False
    
    # Create dummy functions
    def get_player_rating_data(player_name):
        return None
    
    def get_team_max_ratings():
        return []

app = Flask(__name__)

# Create necessary directories
os.makedirs('static/radars', exist_ok=True)

def get_team_logo_url(team_name):
    """Generate logo URL for a team name, handling various name formats"""
    if not team_name:
        return None
    
    # Create potential filename variations
    potential_names = [
        team_name,  # Exact match
        team_name.replace(' ', ' '),  # Handle any spacing issues
        team_name.replace('State', 'St.'),  # Common abbreviation
        team_name.replace('Saint', 'St.'),  # Saint -> St.
        team_name.replace('University', 'U.'),  # University -> U.
    ]
    
    # Check if logo file exists (we'll use a simple approach)
    logo_filename = f"{team_name}.png"
    return f"logos/{logo_filename}"

# Add the helper function to Jinja2 context
@app.context_processor
def utility_processor():
    return dict(get_team_logo_url=get_team_logo_url)

# SQLite DB setup for NCAA data
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data', 'ncaa_soccer.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/')
def home():
    # Get summary statistics for the home page
    with db.engine.connect() as conn:
        # Total matches
        result = conn.execute(text("SELECT COUNT(*) FROM matches"))
        total_matches = result.fetchone()[0]
        
        # Total teams
        result = conn.execute(text("SELECT COUNT(DISTINCT team) FROM players WHERE team IS NOT NULL"))
        total_teams = result.fetchone()[0]
        
        # Total players
        result = conn.execute(text("SELECT COUNT(*) FROM players WHERE name IS NOT NULL"))
        total_players = result.fetchone()[0]
        
        # Total goals
        result = conn.execute(text("SELECT SUM(goals) FROM players"))
        total_goals = result.fetchone()[0] or 0
        
        # Top 5 teams by total goals scored by their players
        result = conn.execute(text("""
            SELECT team, SUM(goals) as total_goals
            FROM players 
            WHERE team IS NOT NULL AND goals > 0
            GROUP BY team 
            ORDER BY total_goals DESC 
            LIMIT 5
        """))
        top_teams = [dict(row._mapping) for row in result]
        
        # Top 5 players by goals
        result = conn.execute(text("""
            SELECT name, team, goals, assists
            FROM players 
            WHERE name IS NOT NULL AND goals > 0
            ORDER BY goals DESC 
            LIMIT 5
        """))
        top_players = [dict(row._mapping) for row in result]
        
        # Recent high-scoring matches
        result = conn.execute(text("""
            SELECT home_team, home_team_score, away_team, away_team_score,
                   (home_team_score + away_team_score) as total_goals
            FROM matches 
            ORDER BY total_goals DESC, ROWID DESC
            LIMIT 10
        """))
        high_scoring_matches = [dict(row._mapping) for row in result]
        
    return render_template("ncaa_index.html", 
                         total_matches=total_matches,
                         total_teams=total_teams,
                         total_players=total_players,
                         total_goals=total_goals,
                         top_teams=top_teams,
                         top_players=top_players,
                         high_scoring_matches=high_scoring_matches)

@app.route('/players')
def show_players():
    page = request.args.get('page', 1, type=int)
    per_page = 100
    offset = (page - 1) * per_page
    
    # Get search and filter parameters
    search_term = request.args.get('search', '').strip()
    team_filter = request.args.get('team', '').strip()
    position_filter = request.args.get('position', '').strip()
    conference_filter = request.args.get('conference', '').strip()
    sort_by = request.args.get('sort', 'goals')
    sort_order = request.args.get('order', 'desc')
    
    # Build WHERE clause
    where_conditions = ["name IS NOT NULL", "team IS NOT NULL", "minutes_played >= 250"]
    params = {"limit": per_page, "offset": offset}
    
    if search_term:
        where_conditions.append("LOWER(name) LIKE :search")
        params['search'] = f"%{search_term.lower()}%"
    
    if team_filter:
        where_conditions.append("team = :team")
        params['team'] = team_filter
    
    # Map position abbreviations to full names
    position_mapping = {
        'F': 'Forward',
        'M': 'Midfielder', 
        'D': 'Defender',
        'G': 'Goalkeeper'
    }
    
    if position_filter:
        # Convert abbreviation to full name if needed
        mapped_position = position_mapping.get(position_filter, position_filter)
        where_conditions.append("position = :position")
        params['position'] = mapped_position
    
    if conference_filter:
        where_conditions.append("conference = :conference")
        params['conference'] = conference_filter
    
    where_clause = " AND ".join(where_conditions)
    
    # Initialize variables to avoid UnboundLocalError
    total_players = 0
    total_pages = 1
    players = []
    teams = []
    
    # Get distinct teams for filter dropdown (needed for all cases)
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT DISTINCT team
            FROM players
            WHERE team IS NOT NULL
            ORDER BY team
        """))
        teams = [row[0] for row in result]
        
        # Get distinct conferences for filter dropdown
        result = conn.execute(text("""
            SELECT DISTINCT conference
            FROM players
            WHERE conference IS NOT NULL
            ORDER BY conference
        """))
        conferences = [row[0] for row in result]
    
    if sort_by == 'max':
        # We need to get all players first, calculate MAX ratings, then sort and paginate
        try:
            if RATINGS_AVAILABLE:
                # Load the player ratings data once
                from player_ratings import load_data, calculate_per90_stats, normalize_stats, calculate_max_ratings
                merged_df, _ = load_data()
                merged_df = calculate_per90_stats(merged_df)
                merged_df = normalize_stats(merged_df)
                merged_df = calculate_max_ratings(merged_df)
                
                # Create a lookup dictionary for MAX ratings
                max_ratings_dict = dict(zip(merged_df['Name'], merged_df['MAX']))
                
                # Get all players that match the filters (without pagination first)
                with db.engine.connect() as conn:
                    all_players_query = f"""
                        SELECT 
                            name,
                            team,
                            position,
                            minutes_played,
                            goals,
                            assists,
                            shots,
                            shots_on_target,
                            fouls_won,
                            CASE 
                                WHEN shots > 0 THEN ROUND(CAST(shots_on_target AS FLOAT) / shots * 100, 1)
                                ELSE 0
                            END as shot_accuracy,
                            CASE 
                                WHEN minutes_played > 0 THEN ROUND(CAST(goals AS FLOAT) / (minutes_played / 90.0), 2)
                                ELSE 0
                            END as goals_per_90
                        FROM players
                        WHERE {where_clause}
                        ORDER BY name ASC
                    """
                    result = conn.execute(text(all_players_query), {k: v for k, v in params.items() if k not in ['limit', 'offset']})
                    all_players = [dict(row._mapping) for row in result]
                
                # Add MAX ratings and sort
                for player in all_players:
                    player['max_rating'] = max_ratings_dict.get(player['name'], 0)
                
                # Sort by MAX rating
                all_players.sort(key=lambda x: x['max_rating'], reverse=(sort_order == 'desc'))
                
                # Apply pagination manually
                total_players = len(all_players)
                total_pages = math.ceil(total_players / per_page) if total_players > 0 else 1
                start_idx = offset
                end_idx = offset + per_page
                players = all_players[start_idx:end_idx]
                
            else:
                # Fallback if ratings not available
                raise Exception("Ratings not available")
                
        except Exception as e:
            print(f"Error with MAX rating sort: {e}")
            # Fallback to regular sorting - continue to else block below
            sort_by = 'goals'  # Change sort type for fallback
            
    if sort_by != 'max':  # Regular sorting (including fallback from MAX rating error)
        # Build ORDER BY clause
        valid_sort_columns = {
            'name': 'name',
            'team': 'team', 
            'position': 'position',
            'goals': 'goals',
            'assists': 'assists',
            'shots': 'shots',
            'goals_per_90': 'CASE WHEN minutes_played > 0 THEN CAST(goals AS FLOAT) / (minutes_played / 90.0) ELSE 0 END',
        }
        
        sort_column = valid_sort_columns.get(sort_by, 'goals')
        sort_direction = 'DESC' if sort_order == 'desc' else 'ASC'
        order_clause = f"ORDER BY {sort_column} {sort_direction}, name ASC"
        
        with db.engine.connect() as conn:
            # Get total count for pagination (with filters)
            count_query = f"""
                SELECT COUNT(*) 
                FROM players
                WHERE {where_clause}
            """
            result = conn.execute(text(count_query), {k: v for k, v in params.items() if k not in ['limit', 'offset']})
            total_players = result.fetchone()[0]
            total_pages = math.ceil(total_players / per_page) if total_players > 0 else 1
            
            # Get players data with pagination, search, and sorting
            main_query = f"""
                SELECT 
                    name,
                    team,
                    position,
                    minutes_played,
                    goals,
                    assists,
                    shots,
                    shots_on_target,
                    fouls_won,
                    CASE 
                        WHEN shots > 0 THEN ROUND(CAST(shots_on_target AS FLOAT) / shots * 100, 1)
                        ELSE 0
                    END as shot_accuracy,
                    CASE 
                        WHEN minutes_played > 0 THEN ROUND(CAST(goals AS FLOAT) / (minutes_played / 90.0), 2)
                        ELSE 0
                    END as goals_per_90
                FROM players
                WHERE {where_clause}
                {order_clause}
                LIMIT :limit OFFSET :offset
            """
            result = conn.execute(text(main_query), params)
            players = [dict(row._mapping) for row in result]
            
            # Add MAX ratings (with error handling for deployment)
            try:
                if RATINGS_AVAILABLE:
                    # Load the player ratings data once
                    from player_ratings import load_data, calculate_per90_stats, normalize_stats, calculate_max_ratings
                    merged_df, _ = load_data()
                    merged_df = calculate_per90_stats(merged_df)
                    merged_df = normalize_stats(merged_df)
                    merged_df = calculate_max_ratings(merged_df)
                    
                    # Create a lookup dictionary for MAX ratings
                    max_ratings_dict = dict(zip(merged_df['Name'], merged_df['MAX']))
                    
                    # Add MAX ratings to players
                    for player in players:
                        player['max_rating'] = max_ratings_dict.get(player['name'], 0)
                else:
                    # Ratings not available, set to N/A
                    for player in players:
                        player['max_rating'] = 'N/A'
                        
            except Exception as e:
                print(f"Error loading MAX ratings: {e}")
                for player in players:
                    player['max_rating'] = 'N/A'
        
    # Calculate pagination info
    has_prev = page > 1
    has_next = page < total_pages
    prev_num = page - 1 if has_prev else None
    next_num = page + 1 if has_next else None
    
    # Generate page numbers for pagination display
    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)
    page_numbers = list(range(start_page, end_page + 1))
    
    return render_template("ncaa_players.html", 
                         players=players, 
                         teams=teams,
                         pagination={
                             'page': page,
                             'per_page': per_page,
                             'total': total_players,
                             'pages': total_pages,
                             'has_prev': has_prev,
                             'has_next': has_next,
                             'prev_num': prev_num,
                             'next_num': next_num,
                             'page_numbers': page_numbers,
                             'start_item': offset + 1 if total_players > 0 else 0,
                             'end_item': min(offset + per_page, total_players)
                         },
                         current_filters={
                             'search': search_term,
                             'team': team_filter,
                             'position': position_filter,
                             'conference': conference_filter,
                             'sort': sort_by,
                             'order': sort_order
                         },
                         conferences=conferences)

@app.route('/teams')
def show_teams():
    with db.engine.connect() as conn:
        # Team standings based on match results
        result = conn.execute(text("""
            SELECT 
                team,
                COUNT(*) as games_played,
                SUM(goals_for) as goals_for,
                SUM(goals_against) as goals_against,
                (SUM(goals_for) - SUM(goals_against)) as goal_difference,
                SUM(wins) as wins,
                SUM(draws) as draws,
                SUM(losses) as losses,
                (SUM(wins) * 3 + SUM(draws)) as points
            FROM (
                SELECT 
                    home_team as team,
                    home_team_score as goals_for,
                    away_team_score as goals_against,
                    CASE WHEN home_team_score > away_team_score THEN 1 ELSE 0 END as wins,
                    CASE WHEN home_team_score = away_team_score THEN 1 ELSE 0 END as draws,
                    CASE WHEN home_team_score < away_team_score THEN 1 ELSE 0 END as losses
                FROM matches
                UNION ALL
                SELECT 
                    away_team as team,
                    away_team_score as goals_for,
                    home_team_score as goals_against,
                    CASE WHEN away_team_score > home_team_score THEN 1 ELSE 0 END as wins,
                    CASE WHEN away_team_score = home_team_score THEN 1 ELSE 0 END as draws,
                    CASE WHEN away_team_score < home_team_score THEN 1 ELSE 0 END as losses
                FROM matches
            ) team_results
            GROUP BY team
            HAVING COUNT(*) >= 5  -- Only teams with at least 5 games
            ORDER BY points DESC, goal_difference DESC, goals_for DESC
        """))
        team_standings = [dict(row._mapping) for row in result]

    # Get team MAX ratings (with error handling)
    try:
        if RATINGS_AVAILABLE:
            team_max_ratings = get_team_max_ratings()
            max_ratings_dict = {team['Team']: {'MAX': team['MAX'], 'ATT': team['ATT'], 'DEF': team['DEF']} for team in team_max_ratings}
        else:
            max_ratings_dict = {}
    except Exception as e:
        print(f"Error loading team ratings: {e}")
        max_ratings_dict = {}
    
    # Add MAX ratings to team standings
    for team in team_standings:
        ratings = max_ratings_dict.get(team['team'], {'MAX': 'N/A', 'ATT': 'N/A', 'DEF': 'N/A'})
        team['max_rating'] = ratings['MAX']
        team['att_rating'] = ratings['ATT']
        team['def_rating'] = ratings['DEF']

    return render_template("ncaa_teams.html", team_standings=team_standings)

@app.route('/matches')
def show_matches():
    page = request.args.get('page', 1, type=int)
    per_page = 50
    offset = (page - 1) * per_page
    
    with db.engine.connect() as conn:
        # Get total count for pagination
        result = conn.execute(text("SELECT COUNT(*) FROM matches"))
        total_matches = result.fetchone()[0]
        total_pages = math.ceil(total_matches / per_page) if total_matches > 0 else 1
        
        # Get matches data with pagination, sorted by date (most recent first)
        result = conn.execute(text("""
            SELECT 
                home_team,
                home_team_score,
                away_team,
                away_team_score,
                home_team_conference,
                away_team_conference,
                (home_team_score + away_team_score) as total_goals,
                CASE 
                    WHEN home_team_score > away_team_score THEN home_team
                    WHEN away_team_score > home_team_score THEN away_team
                    ELSE 'Draw'
                END as winner
            FROM matches
            ORDER BY ROWID DESC
            LIMIT :limit OFFSET :offset
        """), {"limit": per_page, "offset": offset})
        matches = [dict(row._mapping) for row in result]
        
    # Calculate pagination info
    has_prev = page > 1
    has_next = page < total_pages
    prev_num = page - 1 if has_prev else None
    next_num = page + 1 if has_next else None
    
    # Generate page numbers for pagination display
    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)
    page_numbers = list(range(start_page, end_page + 1))
    
    return render_template("ncaa_matches.html", 
                         matches=matches,
                         pagination={
                             'page': page,
                             'per_page': per_page,
                             'total': total_matches,
                             'pages': total_pages,
                             'has_prev': has_prev,
                             'has_next': has_next,
                             'prev_num': prev_num,
                             'next_num': next_num,
                             'page_numbers': page_numbers,
                             'start_item': offset + 1 if total_matches > 0 else 0,
                             'end_item': min(offset + per_page, total_matches)
                         })

@app.route('/player/<player_name>')
def player_profile(player_name):
    # Decode URL-encoded player name
    player_name = unquote(player_name)
    
    with db.engine.connect() as conn:
        # Get player's stats
        result = conn.execute(text("""
            SELECT 
                name,
                team,
                position,
                minutes_played,
                goals,
                assists,
                shots,
                shots_on_target,
                fouls_won,
                CASE 
                    WHEN shots > 0 THEN ROUND(CAST(shots_on_target AS FLOAT) / shots * 100, 1)
                    ELSE 0
                END as shot_accuracy,
                CASE 
                    WHEN minutes_played > 0 THEN ROUND(CAST(goals AS FLOAT) / (minutes_played / 90.0), 2)
                    ELSE 0
                END as goals_per_90,
                CASE 
                    WHEN minutes_played > 0 THEN ROUND(CAST(assists AS FLOAT) / (minutes_played / 90.0), 2)
                    ELSE 0
                END as assists_per_90
            FROM players
            WHERE name = :player_name
        """), {'player_name': player_name})
        
        player_stats = result.fetchone()
        if not player_stats:
            return f"Player '{player_name}' not found", 404
        
        player_data = dict(player_stats._mapping)
        
        # Get MAX rating and radar chart data with timeout protection
        try:
            rating_data = get_player_rating_data(player_name)
            if rating_data:
                player_data['max_rating'] = rating_data.get('MAX', 'N/A')
                player_data['radar_chart'] = rating_data.get('radar_chart', None)
            else:
                player_data['max_rating'] = 'N/A'
                player_data['radar_chart'] = None
        except Exception as e:
            print(f"Error loading rating data for {player_name}: {e}")
            player_data['max_rating'] = 'N/A'
            player_data['radar_chart'] = None
        
        # Get team matches to show team context
        result = conn.execute(text("""
            SELECT 
                home_team,
                home_team_score,
                away_team,
                away_team_score,
                CASE 
                    WHEN home_team = :team THEN 'vs ' || away_team || ' (' || home_team_score || '-' || away_team_score || ')'
                    WHEN away_team = :team THEN 'at ' || home_team || ' (' || away_team_score || '-' || home_team_score || ')'
                END as match_description
            FROM matches
            WHERE home_team = :team OR away_team = :team
            ORDER BY ROWID DESC
            LIMIT 10
        """), {'team': player_data['team']})
        
        team_matches = [dict(row._mapping) for row in result]
        
    return render_template('ncaa_player_profile.html', 
                         player=player_data, 
                         team_matches=team_matches)

@app.route('/team/<team_name>')
def team_profile(team_name):
    team_name = unquote(team_name)
    
    with db.engine.connect() as conn:
        # Team record and stats
        result = conn.execute(text("""
            SELECT 
                team,
                COUNT(*) as games_played,
                SUM(goals_for) as goals_for,
                SUM(goals_against) as goals_against,
                (SUM(goals_for) - SUM(goals_against)) as goal_difference,
                SUM(wins) as wins,
                SUM(draws) as draws,
                SUM(losses) as losses,
                (SUM(wins) * 3 + SUM(draws)) as points
            FROM (
                SELECT 
                    home_team as team,
                    home_team_score as goals_for,
                    away_team_score as goals_against,
                    CASE WHEN home_team_score > away_team_score THEN 1 ELSE 0 END as wins,
                    CASE WHEN home_team_score = away_team_score THEN 1 ELSE 0 END as draws,
                    CASE WHEN home_team_score < away_team_score THEN 1 ELSE 0 END as losses
                FROM matches WHERE home_team = :team_name
                UNION ALL
                SELECT 
                    away_team as team,
                    away_team_score as goals_for,
                    home_team_score as goals_against,
                    CASE WHEN away_team_score > home_team_score THEN 1 ELSE 0 END as wins,
                    CASE WHEN away_team_score = home_team_score THEN 1 ELSE 0 END as draws,
                    CASE WHEN away_team_score < home_team_score THEN 1 ELSE 0 END as losses
                FROM matches WHERE away_team = :team_name
            ) team_results
            WHERE team = :team_name
            GROUP BY team
        """), {'team_name': team_name})
        
        team_stats = result.fetchone()
        if not team_stats:
            # If no match data, create basic stats structure
            team_stats = {
                'team': team_name,
                'games_played': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'goals_for': 0,
                'goals_against': 0,
                'goal_difference': 0,
                'points': 0
            }
        else:
            team_stats = dict(team_stats._mapping)
            
        # Get team roster (all players, including those with <250 minutes)
        result = conn.execute(text("""
            SELECT 
                name,
                position,
                minutes_played,
                goals,
                assists,
                shots,
                shots_on_target,
                fouls_won,
                ROUND(goals * 90.0 / minutes_played, 2) as goals_per_90,
                ROUND(assists * 90.0 / minutes_played, 2) as assists_per_90
            FROM players 
            WHERE team = :team_name AND minutes_played > 0
            ORDER BY minutes_played DESC, goals DESC
        """), {'team_name': team_name})
        roster = [dict(row._mapping) for row in result]
        
        # Get recent matches
        result = conn.execute(text("""
            SELECT 
                home_team,
                home_team_score,
                away_team,
                away_team_score,
                home_team_conference,
                away_team_conference,
                CASE 
                    WHEN home_team = :team_name AND home_team_score > away_team_score THEN 'W'
                    WHEN away_team = :team_name AND away_team_score > home_team_score THEN 'W'
                    WHEN home_team_score = away_team_score THEN 'D'
                    ELSE 'L'
                END as result,
                CASE 
                    WHEN home_team = :team_name THEN away_team
                    ELSE home_team
                END as opponent,
                CASE 
                    WHEN home_team = :team_name THEN 'H'
                    ELSE 'A'
                END as home_away
            FROM matches 
            WHERE home_team = :team_name OR away_team = :team_name
            ORDER BY ROWID DESC
            LIMIT 10
        """), {'team_name': team_name})
        recent_matches = [dict(row._mapping) for row in result]
        
        # Get team MAX rating (with error handling)
        try:
            if RATINGS_AVAILABLE:
                team_max_ratings = get_team_max_ratings()
                team_rating_data = next((team for team in team_max_ratings if team['Team'] == team_name), {'MAX': 'N/A', 'ATT': 'N/A', 'DEF': 'N/A'})
            else:
                team_rating_data = {'MAX': 'N/A', 'ATT': 'N/A', 'DEF': 'N/A'}
        except Exception as e:
            print(f"Error loading team ratings: {e}")
            team_rating_data = {'MAX': 'N/A', 'ATT': 'N/A', 'DEF': 'N/A'}
        
        # Calculate additional team stats
        team_stats['avg_goals_per_game'] = round(team_stats['goals_for'] / max(team_stats['games_played'], 1), 2)
        team_stats['avg_goals_against_per_game'] = round(team_stats['goals_against'] / max(team_stats['games_played'], 1), 2)
        team_stats['total_players'] = len(roster)
        team_stats['active_players'] = len([p for p in roster if p['minutes_played'] >= 250])
        team_stats['max_rating'] = team_rating_data['MAX']
        team_stats['att_rating'] = team_rating_data['ATT']
        team_stats['def_rating'] = team_rating_data['DEF']
        
        return render_template("ncaa_team_profile.html", 
                             team_stats=team_stats,
                             roster=roster,
                             recent_matches=recent_matches)

    return render_template("ncaa_team_profile.html", 
                         team_stats={'team': team_name, 'error': 'Team not found'},
                         roster=[],
                         recent_matches=[])

# Season and Date Management API Endpoints
@app.route('/api/seasons')
def get_available_seasons():
    """Get list of available seasons"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT season, display_name, is_active, data_collection_active
                FROM seasons 
                ORDER BY season DESC
            """))
            seasons = [dict(row._mapping) for row in result]
            return jsonify(seasons)
    except Exception as e:
        print(f"Error fetching seasons: {e}")
        # Fallback to default 2024 season
        return jsonify([{
            'season': '2024',
            'display_name': '2024-25 Season',
            'is_active': False,
            'data_collection_active': False
        }])

@app.route('/api/dates/<season>')
def get_available_dates(season):
    """Get available data dates for a season"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT snapshot_date, description, total_players, is_current
                FROM data_snapshots 
                WHERE season = ?
                ORDER BY snapshot_date DESC
            """), (season,))
            dates = [dict(row._mapping) for row in result]
            return jsonify(dates)
    except Exception as e:
        print(f"Error fetching dates for season {season}: {e}")
        # Fallback for 2024 season
        if season == '2024':
            return jsonify([{
                'snapshot_date': '2024-12-31',
                'description': 'Final 2024 season data',
                'total_players': 6246,  # Approximate from your current data
                'is_current': True
            }])
        return jsonify([])

@app.route('/api/season-status')
def get_season_status():
    """Get current season status and data collection info"""
    try:
        with db.engine.connect() as conn:
            # Get current active season
            result = conn.execute(text("""
                SELECT season, display_name, data_collection_active
                FROM seasons 
                WHERE is_active = TRUE
                LIMIT 1
            """))
            current_season = result.fetchone()
            
            if current_season:
                current_season = dict(current_season._mapping)
            else:
                # Default to 2024 if no active season
                current_season = {
                    'season': '2024',
                    'display_name': '2024-25 Season',
                    'data_collection_active': False
                }
            
            # Get latest data snapshot for current season
            result = conn.execute(text("""
                SELECT snapshot_date, total_players, description
                FROM data_snapshots 
                WHERE season = ? AND is_current = TRUE
                LIMIT 1
            """), (current_season['season'],))
            latest_snapshot = result.fetchone()
            
            if latest_snapshot:
                current_season['latest_data'] = dict(latest_snapshot._mapping)
            
            return jsonify(current_season)
    except Exception as e:
        print(f"Error fetching season status: {e}")
        return jsonify({
            'season': '2024',
            'display_name': '2023-24 Season',
            'data_collection_active': False,
            'latest_data': {
                'snapshot_date': '2024-12-31',
                'total_players': 6246,
                'description': 'Final 2024 season data'
            }
        })

@app.route('/players/<season>')
@app.route('/players/<season>/<date>')
def show_players_historical(season, date='current'):
    """Show players for specific season/date"""
    # For now, redirect to regular players page for 2024 season
    # When 2025 data becomes available, this will handle historical views
    if season == '2024':
        return show_players()  # Use existing function for 2024 data
    else:
        # Future: Handle 2025 and other seasons
        # For now, show message that season data isn't available yet
        return render_template("ncaa_players.html", 
                             players=[], 
                             teams=[],
                             conferences=[],
                             pagination={'page': 1, 'per_page': 100, 'total': 0, 'pages': 1, 
                                       'has_prev': False, 'has_next': False, 'prev_num': None, 
                                       'next_num': None, 'page_numbers': [1], 'start_item': 0, 'end_item': 0},
                             current_filters={'search': '', 'team': '', 'position': '', 'conference': '', 'sort': 'goals', 'order': 'desc'},
                             season_message=f"Data for {season} season is not yet available. Data collection will begin when the season starts.")

if __name__ == '__main__':
    app.run(debug=True)
