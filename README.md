# America Scouted - NCAA Division I Soccer Dashboard

A comprehensive web application for analyzing and visualizing NCAA Division I Men's Soccer performance data for the 2024 season. Built with Flask, SQLite, and advanced analytics featuring proprietary MAX rating system and player performance insights.

## 🚀 Features

### Core Analytics
- **Player Performance**: Comprehensive statistics including goals, assists, shots, and advanced MAX ratings
- **Team Analysis**: Team standings with MAX ratings, ATT/DEF calculations, and linear defense scaling
- **Match Results**: Complete 2024 season match data with scoring analysis
- **Advanced Ratings**: Proprietary MAX rating system with normalized 0-100 scale performance metrics

### Data Visualization
- **Player Profiles**: Individual player radar charts with comprehensive performance visualization
- **Team Profiles**: Detailed team statistics with attacking and defensive ratings
- **Interactive Dashboards**: Sortable tables, advanced filtering, responsive design
- **Radar Charts**: Professional player performance visualization with percentile rankings

### User Experience
- **America Scouted Branding**: Professional branded interface with custom logo integration
- **Bootstrap 5 UI**: Modern, responsive design with Font Awesome icons
- **Advanced Sorting**: Global MAX rating sorting across all players, not just current page
- **Mobile Friendly**: Responsive design optimized for all device sizes
- **Smart Pagination**: 100 players per page with intelligent navigation

## 📊 Data Coverage

- **NCAA Division I**: Complete 2024 season coverage
- **1,900+ Matches**: Comprehensive match results and statistics
- **6,200+ Players**: Players with 250+ minutes (focus on regular contributors)
- **200+ Teams**: Complete NCAA Division I program coverage
- **Advanced Metrics**: Goals per 90, shot accuracy, MAX ratings, ATT/DEF analysis

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, Flask 3.0, SQLAlchemy 2.0
- **Database**: SQLite with optimized queries and indexing
- **Frontend**: HTML5, CSS3, Bootstrap 5, Font Awesome 6
- **Data Processing**: Pandas, NumPy for advanced analytics
- **Visualization**: Matplotlib, Seaborn for radar chart generation
- **Deployment**: Render.com with production-ready configuration

## 🎯 MAX Rating System

Our proprietary MAX rating system provides comprehensive player evaluation:

### Team Ratings
- **STR (Strength)**: `(ATT × 0.5) + ((max_def - DEF) × 0.5)`
- **Linear Defense Scaling**: `max_def - DEF` where lower DEF values = higher defensive strength
- **MAX Rating**: Normalized 0-100 scale for easy comparison

### Player Ratings
- **Per-90 Statistics**: All metrics calculated per 90 minutes for fair comparison
- **Normalized Scoring**: Performance metrics scaled 0-100 for standardization
- **Composite Analysis**: Multiple performance factors combined into single MAX score
- **Percentile Rankings**: Player performance relative to all NCAA Division I players

## 📁 Project Structure

```
soccer-performance-dashboard/
├── ncaa_app.py           # Main Flask application with all routes
├── player_ratings.py     # MAX rating calculations and radar chart generation
├── start.py             # Production server entry point
├── data/                # Database and CSV files
│   ├── ncaa_soccer.db   # SQLite database with players and matches
│   ├── d1_player_stats.csv
│   ├── ncaa_mens_scores_2024.csv
│   └── processed/       # Processed analytics data
├── templates/           # HTML templates with America Scouted branding
│   ├── ncaa_layout.html # Base template with navigation
│   ├── ncaa_index.html  # Home dashboard
│   ├── ncaa_players.html # Player statistics with MAX rating sorting
│   ├── ncaa_teams.html  # Team standings
│   ├── ncaa_matches.html # Match results
│   ├── ncaa_player_profile.html # Individual player profiles
│   └── ncaa_team_profile.html   # Team detail pages
├── static/              # Static assets
│   ├── AmericaScouted-01.png # Brand logo
│   └── radars/          # Generated radar charts
├── Logos_png/           # NCAA team logos (200+ teams)
├── scripts/             # Data processing utilities
├── requirements.txt     # Python dependencies
├── render.yaml         # Render.com deployment configuration
├── runtime.txt         # Python version specification
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip package manager

### Local Development

```bash
# Clone the repository
git clone https://github.com/MaxwellGerhart/soccer-performance-dashboard.git
cd soccer-performance-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the application
python ncaa_app.py
```

### Access the Dashboard
- Open your browser to `http://localhost:5000`
- Navigate through different sections using the top menu

## 🎯 Dashboard Sections

### 1. Home Dashboard
- **Summary Statistics**: Total matches, teams, players, goals
- **Top Scorers**: Leading goal scorers with team information
- **Top Teams**: Highest scoring teams in 2024 season
- **High-Scoring Matches**: Most exciting games of the season

### 2. Player Statistics
- **Comprehensive Metrics**: Goals, assists, shots, accuracy, goals per 90
- **MAX Rating Sorting**: Global sorting across all 6,200+ players
- **Advanced Filtering**: By team, position, search terms
- **Player Profiles**: Click any player name for detailed analysis

### 3. Team Analysis
- **Team Standings**: All NCAA Division I teams with MAX ratings
- **ATT/DEF Ratings**: Attacking and defensive strength analysis
- **Linear Defense Scaling**: Advanced defensive evaluation methodology
- **Team Profiles**: Detailed team pages with roster and statistics

### 4. Match Results
- **Complete 2024 Season**: All NCAA Division I match results
- **Score Analysis**: Goal totals and match outcomes
- **Team Performance**: Home and away performance tracking

### 5. Player Profiles
- **Individual Analysis**: Complete player statistics and performance
- **Radar Charts**: Professional visualization of player strengths
- **Percentile Rankings**: Performance relative to all NCAA Division I players
- **Team Context**: Player performance within team structure

## 📊 Key Features

### Advanced Sorting
- **MAX Rating Global Sort**: Sorts all 6,200+ players, not just current page
- **Database Optimization**: Efficient queries for large datasets
- **Smart Pagination**: Maintains sorting across all pages

### Professional Visualization
- **Radar Charts**: Generated on-demand for player profiles
- **Team Logos**: 200+ NCAA team logos for visual identification
- **America Scouted Branding**: Consistent professional appearance

### Performance Optimization
- **Graceful Degradation**: Works with or without advanced analytics
- **Error Handling**: Robust error handling for production deployment
- **Database Indexing**: Optimized queries for fast performance

## 🚀 Deployment

### Render.com (Production)
```bash
# Automatic deployment from GitHub
# Uses render.yaml configuration
# Python 3.11 with optimized dependencies
```

### Environment Variables
- **PYTHON_VERSION**: 3.11.11
- **PIP_PREFER_BINARY**: 1 (avoid compilation issues)

## � Configuration

### Database
- **SQLite**: `data/ncaa_soccer.db`
- **Tables**: `players`, `matches`
- **Indexes**: Optimized for common queries

### Dependencies
- **Core**: Flask, SQLAlchemy, Gunicorn
- **Analytics**: Pandas, NumPy, Matplotlib, Seaborn
- **UI**: Bootstrap 5, Font Awesome 6

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **NCAA Division I Soccer**: For providing the foundation for collegiate soccer analytics
- **2024 Season Data**: Comprehensive statistics from the complete season
- **Bootstrap** and **Font Awesome** for UI components
- **Flask** community for the excellent web framework
- **Render.com** for reliable hosting platform

---

**America Scouted - Advanced Soccer Analytics**  
*Built by Maxwell Gerhart*
