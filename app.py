from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
from urllib.parse import unquote

app = Flask(__name__)

# SQLite DB setup
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data', 'soccer.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/')
def home():
    # Get summary statistics for the home page
    with db.engine.connect() as conn:
        # Total events
        result = conn.execute(text("SELECT COUNT(*) FROM events"))
        total_events = result.fetchone()[0]
        
        # Total teams
        result = conn.execute(text("SELECT COUNT(DISTINCT team_name) FROM events WHERE team_name IS NOT NULL"))
        total_teams = result.fetchone()[0]
        
        # Total players
        result = conn.execute(text("SELECT COUNT(DISTINCT player_name) FROM events WHERE player_name IS NOT NULL"))
        total_players = result.fetchone()[0]
        
        # Total goals
        result = conn.execute(text("SELECT COUNT(*) FROM events WHERE type_name = 'Shot' AND shot_outcome_name = 'Goal'"))
        total_goals = result.fetchone()[0]
        
        # Top 5 teams by goals
        result = conn.execute(text("""
            SELECT team_name, COUNT(*) as goals
            FROM events 
            WHERE type_name = 'Shot' AND shot_outcome_name = 'Goal' AND team_name IS NOT NULL
            GROUP BY team_name 
            ORDER BY goals DESC 
            LIMIT 5
        """))
        top_teams = [dict(row._mapping) for row in result]
        
        # Top 5 players by goals
        result = conn.execute(text("""
            SELECT player_name, COUNT(*) as goals
            FROM events 
            WHERE type_name = 'Shot' AND shot_outcome_name = 'Goal' AND player_name IS NOT NULL
            GROUP BY player_name 
            ORDER BY goals DESC 
            LIMIT 5
        """))
        top_players = [dict(row._mapping) for row in result]
        
        # Recent events
        result = conn.execute(text("""
            SELECT player_name, team_name, type_name, minute
            FROM events 
            WHERE player_name IS NOT NULL 
            ORDER BY minute DESC 
            LIMIT 10
        """))
        recent_events = [dict(row._mapping) for row in result]
        
    return render_template("index.html", 
                         total_events=total_events,
                         total_teams=total_teams,
                         total_players=total_players,
                         total_goals=total_goals,
                         top_teams=top_teams,
                         top_players=top_players,
                         recent_events=recent_events)

@app.route('/players')
def show_players():
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                e.player_name,
                e.team_name,
                -- Goals scored
                SUM(CASE WHEN e.type_name = 'Shot' AND e.shot_outcome_name = 'Goal' THEN 1 ELSE 0 END) AS goals,
                -- Assists (goal assists)
                SUM(CASE WHEN e.pass_goal_assist = 1 THEN 1 ELSE 0 END) AS assists,
                -- Expected Goals (xG)
                ROUND(SUM(CASE WHEN e.shot_statsbomb_xg IS NOT NULL THEN e.shot_statsbomb_xg ELSE 0 END), 2) AS xg,
                -- Expected Assists (xA) - key passes weighted by conversion rate
                ROUND(COUNT(CASE WHEN e.shot_key_pass_id IS NOT NULL THEN 1 END) * 0.106, 2) AS xa,
                -- Estimate minutes played (simplified)
                COUNT(DISTINCT CONCAT(CAST(e.period AS TEXT), '_', CAST(e.minute AS TEXT))) AS estimated_minutes
            FROM events e
            WHERE e.player_name IS NOT NULL
            GROUP BY e.player_name, e.team_name
            HAVING COUNT(*) > 50  -- Only players with significant involvement
            ORDER BY goals DESC, xg DESC
            LIMIT 50
        """))
        players = [dict(row._mapping) for row in result]
    return render_template("players.html", players=players)


@app.route('/teams')
def show_teams():
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                team_name,
                -- Goals scored by this team
                SUM(CASE WHEN type_name = 'Shot' AND shot_outcome_name = 'Goal' 
                     AND possession_team_name = team_name THEN 1 ELSE 0 END) +
                SUM(CASE WHEN type_name = 'Own Goal For' THEN 1 ELSE 0 END) AS goals_for,
                -- xG for this team
                ROUND(SUM(CASE WHEN shot_statsbomb_xg IS NOT NULL 
                          AND possession_team_name = team_name THEN shot_statsbomb_xg ELSE 0 END), 2) AS xg_for
            FROM events
            WHERE team_name IS NOT NULL
            GROUP BY team_name
            ORDER BY goals_for DESC
        """))
        teams = [dict(row._mapping) for row in result]
        
        return render_template("teams.html", teams=teams)


@app.route('/events')
def show_events():
    with db.engine.connect() as conn:
        result = conn.execute(
            text("SELECT player_name, team_name, type_name, minute FROM events WHERE player_name IS NOT NULL ORDER BY minute DESC LIMIT 100")
        )
        events = [dict(row._mapping) for row in result]
    return render_template("events.html", events=events)

@app.route('/traits')
def show_traits():
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                player_name,
                spatial_awareness_score,
                decision_efficiency_index,
                technical_execution_quotient,
                composite_score,
                total_events
            FROM player_traits
            ORDER BY composite_score DESC
            LIMIT 50
        """))
        traits = [dict(row._mapping) for row in result]
    return render_template("traits.html", traits=traits)

@app.route('/player/<player_name>')
def player_profile(player_name):
    # Decode URL-encoded player name
    player_name = unquote(player_name)
    
    with db.engine.connect() as conn:
        # Get player's basic stats
        result = conn.execute(text("""
            SELECT 
                e.player_name,
                e.team_name,
                -- Goals scored
                SUM(CASE WHEN e.type_name = 'Shot' AND e.shot_outcome_name = 'Goal' THEN 1 ELSE 0 END) AS goals,
                -- Assists (goal assists)
                SUM(CASE WHEN e.pass_goal_assist = 1 THEN 1 ELSE 0 END) AS assists,
                -- Expected Goals (xG)
                ROUND(SUM(CASE WHEN e.shot_statsbomb_xg IS NOT NULL THEN e.shot_statsbomb_xg ELSE 0 END), 2) AS xg,
                -- Expected Assists (xA) - key passes weighted by conversion rate
                ROUND(COUNT(CASE WHEN e.shot_key_pass_id IS NOT NULL THEN 1 END) * 0.106, 2) AS xa,
                -- Shots taken
                SUM(CASE WHEN e.type_name = 'Shot' THEN 1 ELSE 0 END) AS shots,
                -- Passes completed
                SUM(CASE WHEN e.type_name = 'Pass' AND e.pass_outcome_name IS NULL THEN 1 ELSE 0 END) AS passes_completed,
                -- Total passes attempted
                SUM(CASE WHEN e.type_name = 'Pass' THEN 1 ELSE 0 END) AS passes_attempted,
                -- Tackles won
                SUM(CASE WHEN e.type_name = 'Duel' AND e.duel_outcome_name = 'Success' THEN 1 ELSE 0 END) AS tackles_won,
                -- Total events
                COUNT(*) AS total_events
            FROM events e
            WHERE e.player_name = :player_name
            GROUP BY e.player_name, e.team_name
        """), {'player_name': player_name})
        
        player_stats = result.fetchone()
        if not player_stats:
            return render_template('404.html', message=f"Player '{player_name}' not found"), 404
        
        player_data = dict(player_stats._mapping)
        
        # Calculate pass completion percentage
        if player_data['passes_attempted'] > 0:
            player_data['pass_completion'] = round((player_data['passes_completed'] / player_data['passes_attempted']) * 100, 1)
        else:
            player_data['pass_completion'] = 0
        
        # Get player traits if available
        traits_result = conn.execute(text("""
            SELECT 
                spatial_awareness_score,
                decision_efficiency_index,
                technical_execution_quotient,
                composite_score
            FROM player_traits
            WHERE player_name = :player_name
        """), {'player_name': player_name})
        
        traits_data = traits_result.fetchone()
        if traits_data:
            player_data['traits'] = dict(traits_data._mapping)
        else:
            player_data['traits'] = None
        
        # Get recent events for this player
        recent_events_result = conn.execute(text("""
            SELECT type_name, minute, period
            FROM events
            WHERE player_name = :player_name
            ORDER BY period DESC, minute DESC
            LIMIT 10
        """), {'player_name': player_name})
        
        recent_events = [dict(row._mapping) for row in recent_events_result]
        
    return render_template('player_profile.html', 
                         player=player_data, 
                         recent_events=recent_events)

if __name__ == '__main__':
    app.run(debug=True)
