/**
 * Results API
 * 
 * GET /api/results?projectId=X&round=Y - Get all votes for visualization
 * GET /api/results?projectId=X&round=Y&participantId=Z - Include "your vote" highlighting
 */

const { getDb } = require('./db');

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  const sql = getDb();
  const { projectId, round, participantId, code } = req.query;
  
  try {
    let project;
    let activeRound = round;
    
    // Get project by ID or code
    if (code) {
      const projects = await sql`
        SELECT * FROM projects 
        WHERE baseline_code = ${code} OR comparison_code = ${code}
      `;
      project = projects[0];
      if (project) {
        activeRound = project.baseline_code === code ? 'baseline' : 'comparison';
      }
    } else if (projectId) {
      const projects = await sql`SELECT * FROM projects WHERE id = ${projectId}`;
      project = projects[0];
    }
    
    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }
    
    if (!activeRound) {
      activeRound = 'baseline';
    }
    
    // Get tensions
    const tensions = await sql`
      SELECT * FROM tensions 
      WHERE project_id = ${project.id} AND is_hidden = FALSE
      ORDER BY display_order
    `;
    
    // Get all votes for this round
    const votes = await sql`
      SELECT v.*, p.display_name 
      FROM votes v
      JOIN participants p ON v.participant_id = p.id
      WHERE v.project_id = ${project.id} AND v.round = ${activeRound}
    `;
    
    // Get consent points
    const consentPoints = await sql`
      SELECT * FROM consent_points 
      WHERE tension_id IN (SELECT id FROM tensions WHERE project_id = ${project.id})
        AND round = ${activeRound}
    `;
    
    // Build response with vote distribution per tension
    const results = tensions.map(tension => {
      const tensionVotes = votes.filter(v => v.tension_id === tension.id);
      
      // Count votes at each position (0-10)
      const distribution = Array(11).fill(0);
      const voteDetails = [];
      
      tensionVotes.forEach(v => {
        if (v.value >= 0 && v.value <= 10) {
          distribution[v.value]++;
          voteDetails.push({
            position: v.value,
            participantId: v.participant_id,
            displayName: v.display_name,
            isYou: participantId ? v.participant_id === participantId : false
          });
        }
      });
      
      // Calculate average
      let average = null;
      if (tensionVotes.length > 0) {
        const sum = tensionVotes.reduce((acc, v) => acc + v.value, 0);
        average = sum / tensionVotes.length;
      }
      
      // Check for manual consent point override
      const cp = consentPoints.find(c => c.tension_id === tension.id);
      const consentPoint = cp ? parseFloat(cp.value) : average;
      const isManualConsent = cp ? cp.is_manual : false;
      
      // Find "your" vote
      const yourVote = participantId 
        ? tensionVotes.find(v => v.participant_id === participantId)
        : null;
      
      return {
        tension: {
          id: tension.id,
          name: tension.name,
          leftAim: { label: tension.left_aim_label, description: tension.left_aim_description },
          rightAim: { label: tension.right_aim_label, description: tension.right_aim_description }
        },
        voteCount: tensionVotes.length,
        distribution,
        voteDetails,
        average,
        consentPoint,
        isManualConsent,
        yourVote: yourVote ? yourVote.value : null
      };
    });
    
    return res.status(200).json({
      project: {
        id: project.id,
        name: project.name,
        sessionDate: project.session_date,
        comparisonCode: project.comparison_code
      },
      round: activeRound,
      participantCount: new Set(votes.map(v => v.participant_id)).size,
      results
    });
    
  } catch (error) {
    console.error('Results API error:', error);
    return res.status(500).json({ error: 'Database error', details: error.message });
  }
};
