#one time use database initialization script

import sqlite3
import os
from pathlib import Path

REPO_ROOT = os.path.dirname(__file__)
DB_DIR = os.path.join(REPO_ROOT, 'data', 'db')
DB_FILE = os.path.join(DB_DIR, 'dota_ai.db')

SCHEMA_SQL = '''
CREATE TABLE IF NOT EXISTS matches (
    match_id TEXT PRIMARY KEY,
    description TEXT,
    start_time INTEGER,
    duration INTEGER,
    radiant_win BOOLEAN,
    game_mode INTEGER,
    lobby_type INTEGER,
    cluster INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS players (
    account_id INTEGER PRIMARY KEY,
    personaname TEXT,
    avatar TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS player_match_stats (
    match_id TEXT,
    player_name TEXT,
    hero TEXT,
    team TEXT,
    kills INTEGER,
    deaths INTEGER,
    assists INTEGER,
    gold INTEGER,
    net_worth INTEGER,
    items TEXT,
    abilities TEXT,
    win BOOLEAN,
    PRIMARY KEY (match_id, player_name),
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);
'''


def init_db():
    Path(DB_DIR).mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()


def get_connection():
    if not os.path.exists(DB_FILE):
        init_db()
    return sqlite3.connect(DB_FILE)


if __name__ == "__main__":
    print("🏗️ Dota AI Database Manager")
    print(f"📁 Database directory: {DB_DIR}")
    print(f"💾 Database file: {DB_FILE}")
    
    # Check if database already exists
    if os.path.exists(DB_FILE):
        print("⚠️ Database already exists!")
        
        response = input("Do you want to recreate it? This will DELETE all data! (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("🛑 Operation cancelled. Database unchanged.")
            exit(0)
        else:
            print("🗑️ Removing existing database...")
            os.remove(DB_FILE)
    
    # Create the database
    print("🏗️ Creating database...")
    init_db()
    
    # Verify it was created
    if os.path.exists(DB_FILE):
        print("✅ Database created successfully!")
        
        # Show database info
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        print(f"🎯 Database ready at: {DB_FILE}")
        print("\n💡 TIP: You don't need to run this script again unless you want to reset the database.")
    else:
        print("❌ Failed to create database!")
        print(f"Expected location: {DB_FILE}")
