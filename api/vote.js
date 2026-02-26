/**
 * Vote API
 * 
 * POST /api/vote - Submit a vote
 * GET /api/vote?tensionId=X&participantId=Y&round=Z - Get a vote
 */

const { getDb } = require('./db');

function generateId() {
  return 'v_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
}

module.exports = async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  const sql = getDb();
  
  try {
    if (req.method === 'POST') {
      // Submit or update a vote
      const { tensionId, participantId, projectId, round, value } = req.body;
      
      // Validate
      if (!tensionId || !participantId || !projectId || !round || value === undefined) {
        return res.status(400).json({ 
          error: 'Missing required fields: tensionId, participantId, projectId, round, value' 
        });
      }
      
      if (value < 0 || value > 10) {
        return res.status(400).json({ error: 'Value must be between 0 and 10' });
      }
      
      if (!['baseline', 'comparison'].includes(round)) {
        return res.status(400).json({ error: 'Round must be "baseline" or "comparison"' });
      }
      
      // Upsert vote (insert or update if exists)
      const id = generateId();
      const result = await sql`
        INSERT INTO votes (id, tension_id, participant_id, project_id, round, value, submitted_at)
        VALUES (${id}, ${tensionId}, ${participantId}, ${projectId}, ${round}, ${value}, CURRENT_TIMESTAMP)
        ON CONFLICT (tension_id, participant_id, round)
        DO UPDATE SET value = ${value}, updated_at = CURRENT_TIMESTAMP
        RETURNING *
      `;
      
      return res.status(200).json({ 
        success: true, 
        vote: result[0] 
      });
      
    } else if (req.method === 'GET') {
      // Get vote(s)
      const { tensionId, participantId, round, projectId } = req.query;
      
      if (projectId && participantId && round) {
        // Get all votes for a participant in a round
        const votes = await sql`
          SELECT * FROM votes 
          WHERE project_id = ${projectId} 
            AND participant_id = ${participantId} 
            AND round = ${round}
        `;
        return res.status(200).json({ votes });
        
      } else if (tensionId && participantId && round) {
        // Get specific vote
        const votes = await sql`
          SELECT * FROM votes 
          WHERE tension_id = ${tensionId} 
            AND participant_id = ${participantId} 
            AND round = ${round}
        `;
        return res.status(200).json({ vote: votes[0] || null });
        
      } else {
        return res.status(400).json({ 
          error: 'Provide either (projectId, participantId, round) or (tensionId, participantId, round)' 
        });
      }
      
    } else {
      return res.status(405).json({ error: 'Method not allowed' });
    }
    
  } catch (error) {
    console.error('Vote API error:', error);
    return res.status(500).json({ error: 'Database error', details: error.message });
  }
};
