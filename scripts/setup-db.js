/**
 * Database Schema Setup for In/Tension
 * 
 * Run with: node scripts/setup-db.js
 * Requires: DATABASE_URL environment variable
 */

const { neon } = require('@neondatabase/serverless');

const schema = `
-- Projects table
CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  baseline_code TEXT UNIQUE,
  comparison_code TEXT UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Participants table
CREATE TABLE IF NOT EXISTS participants (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  display_name TEXT NOT NULL,
  email_hash TEXT,
  color TEXT,
  joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(project_id, email_hash)
);

-- Tensions table
CREATE TABLE IF NOT EXISTS tensions (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  left_aim_label TEXT NOT NULL,
  left_aim_description TEXT,
  right_aim_label TEXT NOT NULL,
  right_aim_description TEXT,
  display_order INTEGER DEFAULT 0,
  is_hidden BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Votes table
CREATE TABLE IF NOT EXISTS votes (
  id TEXT PRIMARY KEY,
  tension_id TEXT NOT NULL REFERENCES tensions(id) ON DELETE CASCADE,
  participant_id TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  round TEXT NOT NULL CHECK (round IN ('baseline', 'comparison')),
  value INTEGER NOT NULL CHECK (value >= 0 AND value <= 10),
  submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP,
  UNIQUE(tension_id, participant_id, round)
);

-- Consent points table (facilitator overrides)
CREATE TABLE IF NOT EXISTS consent_points (
  id TEXT PRIMARY KEY,
  tension_id TEXT NOT NULL REFERENCES tensions(id) ON DELETE CASCADE,
  round TEXT NOT NULL CHECK (round IN ('baseline', 'comparison')),
  value DECIMAL(4,2) NOT NULL,
  is_manual BOOLEAN DEFAULT TRUE,
  set_by TEXT,
  set_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(tension_id, round)
);

-- Voting sessions table
CREATE TABLE IF NOT EXISTS voting_sessions (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  participant_id TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
  round TEXT NOT NULL CHECK (round IN ('baseline', 'comparison')),
  status TEXT DEFAULT 'in_progress' CHECK (status IN ('not_started', 'in_progress', 'submitted')),
  current_index INTEGER DEFAULT 0,
  started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  submitted_at TIMESTAMP,
  UNIQUE(project_id, participant_id, round)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_votes_tension ON votes(tension_id);
CREATE INDEX IF NOT EXISTS idx_votes_participant ON votes(participant_id);
CREATE INDEX IF NOT EXISTS idx_votes_project_round ON votes(project_id, round);
CREATE INDEX IF NOT EXISTS idx_tensions_project ON tensions(project_id);
CREATE INDEX IF NOT EXISTS idx_participants_project ON participants(project_id);
`;

async function setup() {
  const databaseUrl = process.env.DATABASE_URL;
  
  if (!databaseUrl) {
    console.error('ERROR: DATABASE_URL environment variable is required');
    console.log('');
    console.log('Set it with:');
    console.log('  export DATABASE_URL="postgres://..."');
    console.log('');
    console.log('Or get it from your Vercel project settings.');
    process.exit(1);
  }
  
  console.log('Connecting to Neon database...');
  const sql = neon(databaseUrl);
  
  console.log('Creating schema...');
  await sql(schema);
  
  console.log('✓ Schema created successfully');
  console.log('');
  console.log('Tables:');
  console.log('  - projects');
  console.log('  - participants');
  console.log('  - tensions');
  console.log('  - votes');
  console.log('  - consent_points');
  console.log('  - voting_sessions');
}

setup().catch(err => {
  console.error('Setup failed:', err.message);
  process.exit(1);
});
