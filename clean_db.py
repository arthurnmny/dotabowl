#!/usr/bin/env python3
"""
Database Cleaner - Removes all data from the Dota AI database
"""

import os
import sqlite3
from db import get_connection, DB_FILE

def clean_database():
    """Execute the SQL cleaner script to remove all data."""
    
    if not os.path.exists(DB_FILE):
        print("❌ Database file not found. Nothing to clean.")
        return
    
    # Read the SQL cleaner script
    sql_file = os.path.join(os.path.dirname(__file__), 'db_cleaner.sql')
    
    if not os.path.exists(sql_file):
        print("❌ SQL cleaner file not found.")
        return
    
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("🧹 Cleaning database...")
        print(f"📁 Database: {DB_FILE}")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Execute the cleaning script
        cursor.executescript(sql_script)
        
        # Also clean processed_files table if it exists
        try:
            cursor.execute("DELETE FROM processed_files")
            print("🗑️  Cleared processed_files table")
        except sqlite3.OperationalError:
            pass  # Table doesn't exist, that's fine
        
        # Get the verification results
        cursor.execute("""
            SELECT 'matches' as table_name, COUNT(*) as row_count FROM matches
            UNION ALL
            SELECT 'players' as table_name, COUNT(*) as row_count FROM players  
            UNION ALL
            SELECT 'player_match_stats' as table_name, COUNT(*) as row_count FROM player_match_stats
        """)
        
        results = list(cursor.fetchall())
        
        # Check processed_files table if it exists
        try:
            cursor.execute("SELECT COUNT(*) FROM processed_files")
            processed_count = cursor.fetchone()[0]
            results.append(('processed_files', processed_count))
        except sqlite3.OperationalError:
            results.append(('processed_files', 'N/A (table not found)'))
        
        results = cursor.fetchall()
        
        conn.commit()
        conn.close()
        
        print("✅ Database cleaned successfully!")
        print("\n📊 Verification - Row counts after cleaning:")
        print("-" * 40)
        
        total_rows = 0
        for table_name, row_count in results:
            if isinstance(row_count, int):
                print(f"  {table_name:<20}: {row_count} rows")
                total_rows += row_count
            else:
                print(f"  {table_name:<20}: {row_count}")
        
        print(f"\n🎯 Total rows remaining: {total_rows}")
        
        if total_rows == 0:
            print("✨ Database is completely clean and ready for fresh imports!")
        else:
            print("⚠️  Some data may still remain.")
            
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")

if __name__ == "__main__":
    print("🧹 Dota AI Database Cleaner")
    print("=" * 40)
    
    response = input("⚠️  This will DELETE ALL DATA in the database. Continue? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        clean_database()
    else:
        print("🛑 Operation cancelled. Database unchanged.")