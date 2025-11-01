# Dotabowl - Dota 2 Match Data Analytics

## Overview

## Convert match to json data
1. Setup claude to be able to interpret dota stats screen shots and convert it into json data. Use Claude_prompt.txt to prompt, include a sample json in match_data folder, "match1.json" then it's corresponding imaage from match_images folder, "match1.png".
2. At the end of a dota2 game, screen shot the stats page, then paste into paint and save as png file.
3. Upload the image to claude and have give you the json file.
4. Save the json file, the file name will use the file name as the match name in the data.
5. The json file can be reviewed and edited before being used in the db. There is a match description that currently has a generic placeholder, that shows up in the end dashboard.

## Core Components

- **`import_matches.py`**: Import script that processes JSON match files and stores data in SQLite database
- **`dashboard_app.py`**: Interactive Streamlit dashboard for visualizing match data and player statistics  
- **`db.py`**: Database initialization and schema management
- **`clean_db.py`**: Database cleaning utility to reset data

## Quick Start

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
# Create the database schema, the database will be in the data/db/ folder as dota_ai.db
python db.py
```

### 3. Import Match Data
```bash
# Place JSON match files in match_data/ folder, the file name will be used as match_id
# Run import (automatically detects new files)
python import_matches.py

# Or use the batch file (Windows)
import_matches.bat
```

### 4. Launch Dashboard
```bash
# Start the analytics dashboard - streamlit will 
python -m streamlit run dashboard_app.py
```

## Data Import Process

### Match Data Format
Place JSON files in the `match_data/` folder with the following structure:

```json
{
    "description": "Match description",
    "winning_team": "Radiant",
    "players": [
        {
            "player_name": "PlayerName",
            "hero": "HERO_NAME", 
            "team": "Radiant",
            "winner": true,
            "kills": 10,
            "deaths": 3,
            "assists": 15,
            "net_worth": 25000
        }
    ]
}
```

### Import Features
- **Incremental Imports**: Only processes new or modified files
- **Duplicate Prevention**: Tracks processed files to avoid data duplication
- **Automatic Match IDs**: Uses filename as match identifier (e.g., `match1.json` → `match1`)
- **Data Validation**: Handles malformed JSON gracefully with error reporting

## Dashboard Features

### Match Overview
- Match results and descriptions
- Win/loss tracking by team
- Match timeline and statistics

### Player Analytics
- Comprehensive player statistics table
- Individual player performance tracking
- Kill/Death/Assist ratios
- Net worth analysis

### Team Performance
- Radiant vs Dire win rate analysis
- Average team statistics
- Performance comparison charts

### Interactive Features
- Player selection and detailed views
- Performance trends over time
- Sortable data tables
- Responsive charts and visualizations

## Database Schema

- **matches**: Match metadata (ID, description, winner, timestamps)
- **players**: Player information (account_id, names)  
- **player_match_stats**: Detailed per-match player performance
- **processed_files**: Import tracking to prevent duplicates

## File Structure

```
dotabowl/
├── assets/                 # Dashboard images and assets
├── data/db/               # SQLite database files
├── match_data/            # JSON match files for import
├── venv/                  # Python virtual environment
├── dashboard_app.py       # Main dashboard application
├── import_matches.py      # Match data import script
├── db.py                  # Database management
├── clean_db.py           # Database reset utility
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Utilities

### Database Management
```bash
# Clean all data (reset database)
python clean_db.py

# Recreate database schema
python db.py
```

### Batch Operations
```bash
# Windows batch file for easy importing
import_matches.bat

# View current database contents
python -c "from db import get_connection; # ... custom queries"
```

## Development Notes

- Built with Python 3.11+
- Uses SQLite for local data storage
- Streamlit for web dashboard interface
- Plotly for interactive visualizations
- Pandas for data manipulation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add match data in the specified JSON format
4. Test imports and dashboard functionality
5. Submit a pull request

---

For detailed import instructions, see `MATCH_IMPORT_README.md`
