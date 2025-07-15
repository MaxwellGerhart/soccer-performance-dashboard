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
    return render_template("index.html")

@app.route('/events')
def show_events():
    with db.engine.connect() as conn:
        result = conn.execute(
            text("SELECT player_name, team_name, type_name, minute FROM events LIMIT 50")
        )
        events = [dict(row._mapping) for row in result]
    return render_template("events.html", events=events)

@app.route('/players')
def show_players():
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                player_name,
                SUM(CASE WHEN type_name = 'Shot' THEN 1 ELSE 0 END) AS shots,
                SUM(CASE WHEN type_name = 'Pass' THEN 1 ELSE 0 END) AS passes,
                SUM(CASE WHEN type_name = 'Dribble' THEN 1 ELSE 0 END) AS dribbles,
                SUM(CASE WHEN type_name = 'Tackle' THEN 1 ELSE 0 END) AS tackles
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
                SUM(CASE WHEN type_name = 'Pass' THEN 1 ELSE 0 END) AS total_passes
            FROM events
            WHERE team_name IS NOT NULL
            GROUP BY team_name
            ORDER BY total_passes DESC
            LIMIT 50
        """))
        teams = [dict(row._mapping) for row in result]
    return render_template("teams.html", teams=teams)


if __name__ == '__main__':
    app.run(debug=True)
