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
    
    // For comparison round, fetch BOTH rounds to show side-by-side
    const isComparison = activeRound === 'comparison';
    
    // Get votes for current round (and baseline if comparison)
    const votes = await sql`
      SELECT v.*, p.display_name 
      FROM votes v
      JOIN participants p ON v.participant_id = p.id
      WHERE v.project_id = ${project.id} AND v.round = ${activeRound}
    `;
    
    // Get baseline votes too if this is comparison view
    let baselineVotes = [];
    if (isComparison) {
      baselineVotes = await sql`
        SELECT v.*, p.display_name 
        FROM votes v
        JOIN participants p ON v.participant_id = p.id
        WHERE v.project_id = ${project.id} AND v.round = 'baseline'
      `;
    }
    
    // Get consent points for both rounds
    const consentPoints = await sql`
      SELECT * FROM consent_points 
      WHERE tension_id IN (SELECT id FROM tensions WHERE project_id = ${project.id})
    `;
    
    // Helper to build vote details for a round
    function buildVoteDetails(tensionVotes, round) {
      const distribution = Array(11).fill(0);
      const voteDetails = [];
      
      tensionVotes.forEach(v => {
        if (v.value >= 0 && v.value <= 10) {
          distribution[v.value]++;
          voteDetails.push({
            position: v.value,
            participantId: v.participant_id,
            displayName: v.display_name,
            isYou: participantId ? v.participant_id === participantId : false,
            round: round
          });
        }
      });
      
      let average = null;
      if (tensionVotes.length > 0) {
        const sum = tensionVotes.reduce((acc, v) => acc + v.value, 0);
        average = sum / tensionVotes.length;
      }
      
      return { distribution, voteDetails, average, voteCount: tensionVotes.length };
    }
    
    // Build response with vote distribution per tension
    const results = tensions.map(tension => {
      const tensionVotes = votes.filter(v => v.tension_id === tension.id);
      const primary = buildVoteDetails(tensionVotes, activeRound);
      
      // Check for manual consent point override
      const cp = consentPoints.find(c => c.tension_id === tension.id && c.round === activeRound);
      const consentPoint = cp ? parseFloat(cp.value) : primary.average;
      const isManualConsent = cp ? cp.is_manual : false;
      
      // Find "your" vote
      const yourVote = participantId 
        ? tensionVotes.find(v => v.participant_id === participantId)
        : null;
      
      // Build result object
      const result = {
        tension: {
          id: tension.id,
          name: tension.name,
          leftAim: { label: tension.left_aim_label, description: tension.left_aim_description },
          rightAim: { label: tension.right_aim_label, description: tension.right_aim_description }
        },
        voteCount: primary.voteCount,
        distribution: primary.distribution,
        voteDetails: primary.voteDetails,
        average: primary.average,
        consentPoint,
        isManualConsent,
        yourVote: yourVote ? yourVote.value : null
      };
      
      // Add baseline data for comparison view
      if (isComparison) {
        const baselineTensionVotes = baselineVotes.filter(v => v.tension_id === tension.id);
        const baseline = buildVoteDetails(baselineTensionVotes, 'baseline');
        const baselineCp = consentPoints.find(c => c.tension_id === tension.id && c.round === 'baseline');
        
        result.baseline = {
          voteCount: baseline.voteCount,
          distribution: baseline.distribution,
          voteDetails: baseline.voteDetails,
          average: baseline.average,
          consentPoint: baselineCp ? parseFloat(baselineCp.value) : baseline.average
        };
      }
      
      return result;
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
