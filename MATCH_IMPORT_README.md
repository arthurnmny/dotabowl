# Match Data Import System

This system automatically imports Dota 2 match data from JSON files into the `dota_ai.db` SQLite database.

## How it Works

1. **Add Match Data**: Place new match JSON files in the `match_data/` folder
2. **Run Import**: Execute the import script to add matches to the database
3. **No Duplicates**: The system tracks processed files and prevents duplicates

## Files

- `import_matches.py` - Main import script
- `import_matches.bat` - Windows batch file for easy execution
- `view_db.py` - Database viewer script
- `db.py` - Database initialization and connection

## Usage

### Method 1: Python Script
```bash
python import_matches.py
```

### Method 2: Batch File (Windows)
Double-click `import_matches.bat` or run from command line.

### View Database Contents
```bash
python view_db.py
```

## JSON Format

Match files should follow this format:

```json
{
    "description": "Match description",
    "winning_team": "Radiant",  // or "Dire"
    "players": [
        {
            "player_name": "Player Name",
            "hero": "HERO_NAME",
            "team": "Radiant",     // or "Dire"
            "winner": true,        // or false
            "kills": 10,
            "deaths": 3,
            "assists": 15,
            "net_worth": 25000
        }
        // ... more players
    ]
}
```

## Database Schema

### Tables Created
- **matches**: Match metadata (ID, winner, timestamps)
- **players**: Player information (account_id, name)
- **player_match_stats**: Individual player performance per match
- **processed_files**: Tracks imported files to prevent duplicates

## Features

- ✅ **Duplicate Prevention**: Files are tracked by name and content hash
- ✅ **Incremental Import**: Only new/changed files are processed
- ✅ **Automatic IDs**: Generates consistent match and player IDs
- ✅ **Error Handling**: Graceful handling of malformed files
- ✅ **Statistics**: Shows import summary and database stats

## Running After Each Match

1. Save match data as JSON in `match_data/` (e.g., `match2.json`, `match3.json`)
2. Run `import_matches.bat` or `python import_matches.py`
3. The script will:
   - Detect new files
   - Import only new match data
   - Skip already processed files
   - Show summary statistics

## Troubleshooting

- **"No JSON files found"**: Ensure files are in `match_data/` with `.json` extension
- **"Already processed"**: File has been imported before (this is normal)
- **"Error reading file"**: Check JSON syntax and encoding (should be UTF-8)

## Example Workflow

```bash
# After Match 1
# 1. Save match1.json to match_data/
# 2. Run import
python import_matches.py
# Result: 1 match imported

# After Match 2  
# 1. Save match2.json to match_data/
# 2. Run import again
python import_matches.py
# Result: 1 new match imported (match1 skipped)

# View all data
python view_db.py
# Shows both matches and all players
```

The system is designed to be run repeatedly without issues - it will always process only new or changed files.