-- SQL script to delete all existing data from Dota AI database
-- This will clean all tables while preserving the schema structure

-- Disable foreign key constraints temporarily to avoid deletion order issues
PRAGMA foreign_keys = OFF;

-- Delete all player match statistics
DELETE FROM player_match_stats;

-- Delete all matches  
DELETE FROM matches;

-- Delete all players
DELETE FROM players;

-- Re-enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Vacuum to reclaim space and optimize database
VACUUM;
