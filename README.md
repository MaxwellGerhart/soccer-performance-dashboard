# Soccer Performance Dashboard

A comprehensive web application for analyzing and visualizing soccer performance data from the FIFA World Cup 2022. Built with Flask, SQLite, and advanced analytics featuring StatsBomb open data.

## 🚀 Features

### Core Analytics
- **Player Performance**: Goals, assists, xG, xA metrics with detailed player profiles
- **Team Statistics**: Goals scored, expected goals (xG), comprehensive team analysis
- **Advanced Traits**: Spatial Awareness Score (SAS), Decision Efficiency Index (DEI), Technical Execution Quotient (TEQ)
- **Interactive Dashboards**: Sortable tables, clickable player profiles, responsive design

### Data Visualization
- **Player Profiles**: Individual player statistics with comprehensive metrics
- **Team Comparison**: Side-by-side team performance analysis
- **Trait Analysis**: Advanced player trait scoring and composite metrics
- **Event Tracking**: Real-time match event monitoring

### User Experience
- **Bootstrap 5 UI**: Modern, responsive design with Font Awesome icons
- **Dynamic Navigation**: Seamless navigation between players, teams, and traits
- **Sortable Tables**: Interactive sorting for all statistical displays
- **Mobile Friendly**: Responsive design for all device sizes

## 📊 Data Sources

- **StatsBomb Open Data**: FIFA World Cup 2022 event data
- **Event Coverage**: 234,652+ events across 32 teams and 680+ players
- **Match Analysis**: Complete tournament coverage with advanced metrics

## 🛠️ Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Database**: SQLite with advanced analytics
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5, Font Awesome
- **Data Processing**: Pandas, NumPy
- **Analytics**: Custom trait calculation algorithms

## 📁 Project Structure

```
soccer-performance-dashboard/
├── app.py                 # Main Flask application
├── templates/            # HTML templates
│   ├── layout.html       # Base template
│   ├── index.html        # Home dashboard
│   ├── players.html      # Player statistics
│   ├── teams.html        # Team statistics
│   ├── traits.html       # Advanced traits
│   └── player_profile.html # Individual player profiles
├── static/              # CSS, JS, images
├── data/               # Database and processed data
│   ├── soccer.db       # SQLite database
│   └── processed/      # Processed CSV files
├── scripts/            # Data processing scripts
│   ├── load_statsbomb.py
│   └── save_to_sqlite.py
└── requirements.txt    # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/MaxwellGerhart/soccer-performance-dashboard.git
cd soccer-performance-dashboard

# Install dependencies
pip install -r requirements.txt

# Set up the database (if not already done)
python scripts/load_statsbomb.py
python scripts/save_to_sqlite.py

# Calculate advanced player traits
python player_traits.py

# Run the application
python app.py
```

### Access the Dashboard
- Open your browser to `http://localhost:5000`
- Navigate through different sections using the top menu

## 📈 Key Metrics Explained

### Basic Statistics
- **Goals**: Total goals scored
- **Assists**: Goal assists provided
- **xG**: Expected Goals based on shot quality
- **xA**: Expected Assists based on key passes

### Advanced Traits
- **SAS (Spatial Awareness Score)**: Measures positioning and space utilization
- **DEI (Decision Efficiency Index)**: Evaluates decision-making under pressure
- **TEQ (Technical Execution Quotient)**: Assesses technical skill execution
- **Composite Score**: Overall performance rating combining all traits

## 🔧 Usage

### Navigation
- **Home**: Overview statistics and top performers
- **Players**: Detailed player statistics with profile links
- **Teams**: Team performance metrics and comparisons
- **Traits**: Advanced analytics and player trait analysis

### Interactive Features
- Click player names to view detailed profiles
- Sort tables by any column (ascending/descending)
- Responsive design adapts to screen size

## 🎯 Dashboard Sections

### 1. Home Dashboard
- Tournament overview statistics
- Top 5 teams and players by goals
- Recent match events
- Quick navigation to all sections

### 2. Player Statistics
- Comprehensive player metrics
- Goals, assists, xG, xA for all players
- Clickable names for detailed profiles
- Sortable by any metric

### 3. Team Analysis
- Team-level performance metrics
- Goals scored and expected goals
- Sortable team comparison

### 4. Advanced Traits
- Sophisticated player analysis
- Custom-developed trait scoring
- Composite performance ratings

### 5. Player Profiles
- Individual player deep-dive
- Complete statistics and traits
- Recent match activity
- Performance summaries

## 🔍 Data Processing

The application processes StatsBomb World Cup 2022 data including:
- Match events and player actions
- Shot data with xG calculations
- Pass completion and key pass metrics
- Advanced spatial and temporal analysis

## 📊 Analytics Features

- **Real-time Calculations**: Dynamic metric computation
- **Advanced Filtering**: Significant player involvement filtering
- **Comparative Analysis**: Player and team comparisons
- **Trait Development**: Custom analytical frameworks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **StatsBomb** for providing open World Cup 2022 data
- **FIFA World Cup 2022** for the incredible tournament
- **Bootstrap** and **Font Awesome** for UI components
- **Flask** community for the excellent web framework

---

**Built by Maxwell Gerhart**
