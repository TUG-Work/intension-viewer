/**
 * Voting Session API
 * 
 * POST /api/session - Create or join a voting session
 * GET /api/session?id=X - Get session details
 * PUT /api/session - Update session (submit, change index)
 */

const { getDb } = require('./db');

function generateId() {
  return 's_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
}

function generateParticipantId() {
  return 'p_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
}

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  const sql = getDb();
  
  try {
    if (req.method === 'POST') {
      // Create or join a voting session
      const { projectId, displayName, round } = req.body;
      
      if (!projectId || !displayName || !round) {
        return res.status(400).json({ 
          error: 'Missing required fields: projectId, displayName, round' 
        });
      }
      
      // Create participant
      const participantId = generateParticipantId();
      await sql`
        INSERT INTO participants (id, project_id, display_name, joined_at)
        VALUES (${participantId}, ${projectId}, ${displayName}, CURRENT_TIMESTAMP)
      `;
      
      // Create session
      const sessionId = generateId();
      await sql`
        INSERT INTO voting_sessions (id, project_id, participant_id, round, status, current_index, started_at)
        VALUES (${sessionId}, ${projectId}, ${participantId}, ${round}, 'in_progress', 0, CURRENT_TIMESTAMP)
      `;
      
      // Get project tensions
      const tensions = await sql`
        SELECT * FROM tensions 
        WHERE project_id = ${projectId} AND is_hidden = FALSE
        ORDER BY display_order
      `;
      
      return res.status(200).json({
        session: {
          id: sessionId,
          projectId,
          participantId,
          displayName,
          round,
          status: 'in_progress',
          currentIndex: 0
        },
        tensions: tensions.map(t => ({
          id: t.id,
          name: t.name,
          leftAim: { label: t.left_aim_label, description: t.left_aim_description },
          rightAim: { label: t.right_aim_label, description: t.right_aim_description }
        }))
      });
      
    } else if (req.method === 'GET') {
      // Get session details
      const { id } = req.query;
      
      if (!id) {
        return res.status(400).json({ error: 'Session id required' });
      }
      
      const sessions = await sql`
        SELECT vs.*, p.display_name 
        FROM voting_sessions vs
        JOIN participants p ON vs.participant_id = p.id
        WHERE vs.id = ${id}
      `;
      
      if (sessions.length === 0) {
        return res.status(404).json({ error: 'Session not found' });
      }
      
      const session = sessions[0];
      
      // Get tensions
      const tensions = await sql`
        SELECT * FROM tensions 
        WHERE project_id = ${session.project_id} AND is_hidden = FALSE
        ORDER BY display_order
      `;
      
      // Get existing votes
      const votes = await sql`
        SELECT tension_id, value FROM votes
        WHERE participant_id = ${session.participant_id} AND round = ${session.round}
      `;
      
      const voteMap = {};
      votes.forEach(v => { voteMap[v.tension_id] = v.value; });
      
      return res.status(200).json({
        session: {
          id: session.id,
          projectId: session.project_id,
          participantId: session.participant_id,
          displayName: session.display_name,
          round: session.round,
          status: session.status,
          currentIndex: session.current_index
        },
        tensions: tensions.map(t => ({
          id: t.id,
          name: t.name,
          leftAim: { label: t.left_aim_label, description: t.left_aim_description },
          rightAim: { label: t.right_aim_label, description: t.right_aim_description }
        })),
        votes: voteMap
      });
      
    } else if (req.method === 'PUT') {
      // Update session
      const { id, status, currentIndex } = req.body;
      
      if (!id) {
        return res.status(400).json({ error: 'Session id required' });
      }
      
      const updates = [];
      const values = {};
      
      if (status === 'submitted') {
        await sql`
          UPDATE voting_sessions 
          SET status = 'submitted', submitted_at = CURRENT_TIMESTAMP
          WHERE id = ${id}
        `;
      } else if (currentIndex !== undefined) {
        await sql`
          UPDATE voting_sessions 
          SET current_index = ${currentIndex}
          WHERE id = ${id}
        `;
      }
      
      return res.status(200).json({ success: true });
      
    } else {
      return res.status(405).json({ error: 'Method not allowed' });
    }
    
  } catch (error) {
    console.error('Session API error:', error);
    return res.status(500).json({ error: 'Database error', details: error.message });
  }
};
