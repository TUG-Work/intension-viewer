/**
 * Database Schema Setup for In/Tension
 * 
 * Run with: node scripts/setup-db.js
 * Requires: DATABASE_URL environment variable
 */

const { neon } = require('@neondatabase/serverless');

async function setup() {
  const databaseUrl = process.env.DATABASE_URL;
  
  if (!databaseUrl) {
    console.error('ERROR: DATABASE_URL environment variable is required');
    process.exit(1);
  }
  
  console.log('Connecting to Neon database...');
  const sql = neon(databaseUrl);
  
  console.log('Creating tables...');
  
  // Projects table
  console.log('  - projects');
  await sql`
    CREATE TABLE IF NOT EXISTS projects (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      session_date DATE,
      baseline_code TEXT UNIQUE,
      comparison_code TEXT UNIQUE,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `;
  
  // Participants table
  console.log('  - participants');
  await sql`
    CREATE TABLE IF NOT EXISTS participants (
      id TEXT PRIMARY KEY,
      project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
      display_name TEXT NOT NULL,
      email_hash TEXT,
      color TEXT,
      joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `;
  
  // Add unique constraint separately (in case table already exists)
  try {
    await sql`CREATE UNIQUE INDEX IF NOT EXISTS participants_project_email ON participants(project_id, email_hash)`;
  } catch (e) { /* ignore if exists */ }
  
  // Tensions table
  console.log('  - tensions');
  await sql`
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
    )
  `;
  
  // Votes table
  console.log('  - votes');
  await sql`
    CREATE TABLE IF NOT EXISTS votes (
      id TEXT PRIMARY KEY,
      tension_id TEXT NOT NULL REFERENCES tensions(id) ON DELETE CASCADE,
      participant_id TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
      project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
      round TEXT NOT NULL,
      value INTEGER NOT NULL,
      submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP
    )
  `;
  
  try {
    await sql`CREATE UNIQUE INDEX IF NOT EXISTS votes_unique ON votes(tension_id, participant_id, round)`;
  } catch (e) { /* ignore if exists */ }
  
  // Consent points table
  console.log('  - consent_points');
  await sql`
    CREATE TABLE IF NOT EXISTS consent_points (
      id TEXT PRIMARY KEY,
      tension_id TEXT NOT NULL REFERENCES tensions(id) ON DELETE CASCADE,
      round TEXT NOT NULL,
      value DECIMAL(4,2) NOT NULL,
      is_manual BOOLEAN DEFAULT TRUE,
      set_by TEXT,
      set_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `;
  
  try {
    await sql`CREATE UNIQUE INDEX IF NOT EXISTS consent_points_unique ON consent_points(tension_id, round)`;
  } catch (e) { /* ignore if exists */ }
  
  // Voting sessions table
  console.log('  - voting_sessions');
  await sql`
    CREATE TABLE IF NOT EXISTS voting_sessions (
      id TEXT PRIMARY KEY,
      project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
      participant_id TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE,
      round TEXT NOT NULL,
      status TEXT DEFAULT 'in_progress',
      current_index INTEGER DEFAULT 0,
      started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      submitted_at TIMESTAMP
    )
  `;
  
  try {
    await sql`CREATE UNIQUE INDEX IF NOT EXISTS sessions_unique ON voting_sessions(project_id, participant_id, round)`;
  } catch (e) { /* ignore if exists */ }
  
  // Create indexes
  console.log('Creating indexes...');
  try {
    await sql`CREATE INDEX IF NOT EXISTS idx_votes_tension ON votes(tension_id)`;
    await sql`CREATE INDEX IF NOT EXISTS idx_votes_participant ON votes(participant_id)`;
    await sql`CREATE INDEX IF NOT EXISTS idx_votes_project_round ON votes(project_id, round)`;
    await sql`CREATE INDEX IF NOT EXISTS idx_tensions_project ON tensions(project_id)`;
    await sql`CREATE INDEX IF NOT EXISTS idx_participants_project ON participants(project_id)`;
  } catch (e) { /* ignore if exists */ }
  
  console.log('');
  console.log('✓ Schema created successfully');
}

setup().catch(err => {
  console.error('Setup failed:', err.message);
  process.exit(1);
});
