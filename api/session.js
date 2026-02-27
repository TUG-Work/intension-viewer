/**
 * Voting Session API
 * 
 * POST /api/session - Create or join a voting session
 * GET /api/session?id=X - Get session details
 * PUT /api/session - Update session (submit, change index)
 */

const { getDb } = require('./db');

function generateId(prefix = 's_') {
  return prefix + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
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
      const { projectId, displayName, email, round } = req.body;
      
      if (!projectId || !displayName || !round) {
        return res.status(400).json({ 
          error: 'Missing required fields: projectId, displayName, round' 
        });
      }
      
      let participantId;
      
      // If email provided, try to find existing global participant
      if (email) {
        const existing = await sql`
          SELECT id FROM participants WHERE email = ${email.toLowerCase()}
        `;
        
        if (existing.length > 0) {
          participantId = existing[0].id;
          // Update display name if changed
          await sql`
            UPDATE participants SET display_name = ${displayName}
            WHERE id = ${participantId}
          `;
        }
      }
      
      // Create new global participant if not found
      if (!participantId) {
        participantId = generateId('usr_');
        await sql`
          INSERT INTO participants (id, email, display_name, created_at)
          VALUES (${participantId}, ${email ? email.toLowerCase() : null}, ${displayName}, CURRENT_TIMESTAMP)
        `;
      }
      
      // Check if already participating in this project
      const existingPP = await sql`
        SELECT id FROM project_participants 
        WHERE participant_id = ${participantId} AND project_id = ${projectId}
      `;
      
      let projectParticipantId;
      if (existingPP.length > 0) {
        projectParticipantId = existingPP[0].id;
        // Update last active
        await sql`
          UPDATE project_participants SET last_active_at = CURRENT_TIMESTAMP
          WHERE id = ${projectParticipantId}
        `;
      } else {
        // Create project participation
        projectParticipantId = generateId('pp_');
        await sql`
          INSERT INTO project_participants (id, participant_id, project_id, role, status, joined_at, last_active_at)
          VALUES (${projectParticipantId}, ${participantId}, ${projectId}, 'participant', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        `;
      }
      
      // Check for existing session in this round
      const existingSession = await sql`
        SELECT id, status, current_index FROM voting_sessions
        WHERE project_id = ${projectId} AND participant_id = ${participantId} AND round = ${round}
      `;
      
      let sessionId, sessionStatus, currentIndex;
      
      if (existingSession.length > 0) {
        // Resume existing session
        sessionId = existingSession[0].id;
        sessionStatus = existingSession[0].status;
        currentIndex = existingSession[0].current_index;
      } else {
        // Create new session
        sessionId = generateId('s_');
        sessionStatus = 'in_progress';
        currentIndex = 0;
        
        await sql`
          INSERT INTO voting_sessions (id, project_id, participant_id, round, status, current_index, started_at)
          VALUES (${sessionId}, ${projectId}, ${participantId}, ${round}, 'in_progress', 0, CURRENT_TIMESTAMP)
        `;
      }
      
      // Get project tensions
      const tensions = await sql`
        SELECT * FROM tensions 
        WHERE project_id = ${projectId} AND is_hidden = FALSE
        ORDER BY display_order
      `;
      
      // Get existing votes for this session
      const votes = await sql`
        SELECT tension_id, value FROM votes
        WHERE participant_id = ${participantId} AND project_id = ${projectId} AND round = ${round}
      `;
      
      const voteMap = {};
      votes.forEach(v => { voteMap[v.tension_id] = v.value; });
      
      return res.status(200).json({
        session: {
          id: sessionId,
          projectId,
          participantId,
          projectParticipantId,
          displayName,
          round,
          status: sessionStatus,
          currentIndex,
          isReturning: existingSession.length > 0
        },
        tensions: tensions.map(t => ({
          id: t.id,
          name: t.name,
          leftAim: { label: t.left_aim_label, description: t.left_aim_description },
          rightAim: { label: t.right_aim_label, description: t.right_aim_description }
        })),
        votes: voteMap
      });
      
    } else if (req.method === 'GET') {
      // Get session details
      const { id } = req.query;
      
      if (!id) {
        return res.status(400).json({ error: 'Session id required' });
      }
      
      const sessions = await sql`
        SELECT vs.*, p.display_name, p.email
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
          email: session.email,
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
      
      if (status === 'submitted') {
        await sql`
          UPDATE voting_sessions 
          SET status = 'submitted', submitted_at = CURRENT_TIMESTAMP
          WHERE id = ${id}
        `;
        
        // Also update project_participants status
        const session = await sql`SELECT participant_id, project_id FROM voting_sessions WHERE id = ${id}`;
        if (session.length > 0) {
          await sql`
            UPDATE project_participants 
            SET status = 'completed', last_active_at = CURRENT_TIMESTAMP
            WHERE participant_id = ${session[0].participant_id} AND project_id = ${session[0].project_id}
          `;
        }
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
