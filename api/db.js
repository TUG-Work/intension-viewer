/**
 * Database connection helper
 */

const { neon } = require('@neondatabase/serverless');

let sql;

function getDb() {
  if (!sql) {
    const databaseUrl = process.env.DATABASE_URL;
    if (!databaseUrl) {
      throw new Error('DATABASE_URL environment variable is required');
    }
    sql = neon(databaseUrl);
  }
  return sql;
}

module.exports = { getDb };
