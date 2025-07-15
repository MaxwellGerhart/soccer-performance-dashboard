from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

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
                player_name,
                SUM(CASE WHEN type_name = 'Shot' THEN 1 ELSE 0 END) AS shots,
                SUM(CASE WHEN type_name = 'Pass' THEN 1 ELSE 0 END) AS passes,
                SUM(CASE WHEN type_name = 'Dribble' THEN 1 ELSE 0 END) AS dribbles,
                SUM(CASE WHEN type_name = 'Duel' AND duel_type_name = 'Tackle' 
                     AND duel_outcome_name IN ('Won', 'Success In Play', 'Success Out') THEN 1 ELSE 0 END) AS tackles,
                SUM(CASE WHEN type_name = 'Interception' THEN 1 ELSE 0 END) AS interceptions,
                SUM(CASE WHEN type_name = 'Ball Recovery' THEN 1 ELSE 0 END) AS ball_recoveries
            FROM events
            WHERE player_name IS NOT NULL
            GROUP BY player_name
            ORDER BY passes DESC
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
                COUNT(*) AS total_events,
                SUM(CASE WHEN type_name = 'Shot' THEN 1 ELSE 0 END) AS total_shots,
                SUM(CASE WHEN type_name = 'Pass' THEN 1 ELSE 0 END) AS total_passes,
                SUM(CASE WHEN type_name = 'Duel' AND duel_type_name = 'Tackle' 
                     AND duel_outcome_name IN ('Won', 'Success In Play', 'Success Out') THEN 1 ELSE 0 END) AS total_tackles,
                SUM(CASE WHEN type_name = 'Interception' THEN 1 ELSE 0 END) AS total_interceptions
            FROM events
            WHERE team_name IS NOT NULL
            GROUP BY team_name
            ORDER BY total_passes DESC
            LIMIT 50
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

if __name__ == '__main__':
    app.run(debug=True)
