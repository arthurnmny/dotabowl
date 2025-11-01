#!/usr/bin/env python3
"""
Match Data Importer for Dota AI Database

This script imports match data from JSON files in the match_data folder
into the dota_ai.db database. It handles incremental imports and prevents
duplicates by tracking processed files.
"""

import os
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from db import get_connection, init_db

# Directory containing match JSON files
MATCH_DATA_DIR = os.path.join(os.path.dirname(__file__), 'match_data')

# Track processed files to prevent duplicates
PROCESSED_FILES_TABLE = '''
CREATE TABLE IF NOT EXISTS processed_files (
    file_name TEXT PRIMARY KEY,
    file_hash TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''


def get_file_hash(file_path: str) -> str:
    """Generate SHA256 hash of file content to detect changes."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def ensure_processed_files_table():
    """Create the processed_files table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(PROCESSED_FILES_TABLE)
    conn.commit()
    conn.close()


def is_file_processed(file_name: str, file_hash: str) -> bool:
    """Check if a file has already been processed."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT file_hash FROM processed_files WHERE file_name = ?",
        (file_name,)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result is None:
        return False
    
    # Check if file content has changed
    return result[0] == file_hash


def mark_file_processed(file_name: str, file_hash: str):
    """Mark a file as processed."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT OR REPLACE INTO processed_files (file_name, file_hash) VALUES (?, ?)",
        (file_name, file_hash)
    )
    conn.commit()
    conn.close()


def generate_match_id(match_data: Dict[str, Any], file_name: str) -> str:
    """Generate match ID from filename (without extension)."""
    return os.path.splitext(file_name)[0]


def add_player_if_not_exists(cursor: sqlite3.Cursor, player_name: str):
    """Add player to players table if they don't exist."""
    # Generate a consistent account_id from player name
    account_id = abs(hash(player_name)) % 1000000000
    
    cursor.execute(
        "INSERT OR IGNORE INTO players (account_id, personaname) VALUES (?, ?)",
        (account_id, player_name)
    )


def import_match_data(file_path: str) -> bool:
    """Import match data from a JSON file into the database."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            match_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Generate match ID
        file_name = os.path.basename(file_path)
        match_id = generate_match_id(match_data, file_name)
        
        # Check if match already exists
        cursor.execute("SELECT match_id FROM matches WHERE match_id = ?", (match_id,))
        if cursor.fetchone():
            print(f"⚠️  Match {match_id} already exists in database, skipping...")
            conn.close()
            return True
        
        # Insert match record
        radiant_win = match_data['winning_team'].lower() == 'radiant'
        
        cursor.execute("""
            INSERT INTO matches (
                match_id, description, start_time, duration, radiant_win, 
                game_mode, lobby_type, cluster
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            match_id,
            match_data.get('description', ''),  # Get description from JSON
            int(datetime.now().timestamp()),  # Default start time
            0,  # Duration not available in current format
            radiant_win,
            22,  # Default game mode (All Pick)
            0,  # Default lobby type
            0   # Default cluster
        ))
        
        # Process each player
        for player in match_data['players']:
            # Add player to players table if they don't exist
            add_player_if_not_exists(cursor, player['player_name'])
            
            # Insert player match stats
            cursor.execute("""
                INSERT INTO player_match_stats (
                    match_id, player_name, hero, team, kills, deaths, assists,
                    gold, net_worth, items, abilities, win
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id,
                player['player_name'],
                player['hero'],
                player['team'],
                player['kills'],
                player['deaths'],
                player['assists'],
                0,  # Gold not available
                player['net_worth'],
                '',  # Items not available
                '',  # Abilities not available
                player['winner']
            ))
        
        conn.commit()
        print(f"✅ Successfully imported match {match_id} from {file_name}")
        print(f"   - Winner: {match_data['winning_team']}")
        print(f"   - Players: {len(match_data['players'])}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error importing match from {file_path}: {e}")
        return False
    finally:
        conn.close()


def import_all_matches():
    """Import all unprocessed match files from the match_data directory."""
    if not os.path.exists(MATCH_DATA_DIR):
        print(f"❌ Match data directory not found: {MATCH_DATA_DIR}")
        return
    
    # Ensure database and processed files table exist
    init_db()
    ensure_processed_files_table()
    
    # Find all JSON files
    json_files = []
    for file_name in os.listdir(MATCH_DATA_DIR):
        if file_name.endswith('.json'):
            json_files.append(file_name)
    
    if not json_files:
        print("📂 No JSON files found in match_data directory")
        return
    
    print(f"🔍 Found {len(json_files)} JSON files in match_data directory")
    
    processed_count = 0
    skipped_count = 0
    
    for file_name in sorted(json_files):
        file_path = os.path.join(MATCH_DATA_DIR, file_name)
        file_hash = get_file_hash(file_path)
        
        # Check if already processed
        if is_file_processed(file_name, file_hash):
            print(f"⏭️  Skipping {file_name} (already processed)")
            skipped_count += 1
            continue
        
        print(f"📥 Processing {file_name}...")
        
        if import_match_data(file_path):
            mark_file_processed(file_name, file_hash)
            processed_count += 1
        else:
            print(f"❌ Failed to process {file_name}")
    
    print(f"\n📊 Import Summary:")
    print(f"   - Processed: {processed_count} files")
    print(f"   - Skipped: {skipped_count} files")
    print(f"   - Total: {len(json_files)} files")


def show_database_stats():
    """Show current database statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Count matches
    cursor.execute("SELECT COUNT(*) FROM matches")
    match_count = cursor.fetchone()[0]
    
    # Count players
    cursor.execute("SELECT COUNT(*) FROM players")
    player_count = cursor.fetchone()[0]
    
    # Count player match stats
    cursor.execute("SELECT COUNT(*) FROM player_match_stats")
    stats_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n📊 Database Statistics:")
    print(f"   - Matches: {match_count}")
    print(f"   - Players: {player_count}")
    print(f"   - Player Match Records: {stats_count}")


if __name__ == "__main__":
    print("🎮 Dota AI Match Data Importer")
    print("=" * 40)
    
    import_all_matches()
    show_database_stats()
    
    print("\n✨ Import complete!")
    print("\n💡 This script can be run repeatedly - it will only process new or changed files.")