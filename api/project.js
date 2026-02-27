/**
 * Project API
 * 
 * GET /api/project?id=X - Get project details with tensions
 * POST /api/project - Create a project
 */

const { getDb } = require('./db');

function generateId() {
  return 'proj_' + Math.random().toString(36).substr(2, 9);
}

function generateCode() {
  return Math.random().toString(36).substr(2, 6).toUpperCase();
}

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  const sql = getDb();
  
  try {
    if (req.method === 'GET') {
      const { id, code } = req.query;
      
      let project;
      
      if (id) {
        const projects = await sql`SELECT * FROM projects WHERE id = ${id}`;
        project = projects[0];
      } else if (code) {
        const projects = await sql`
          SELECT * FROM projects 
          WHERE baseline_code = ${code} OR comparison_code = ${code}
        `;
        project = projects[0];
      } else {
        return res.status(400).json({ error: 'Provide id or code' });
      }
      
      if (!project) {
        return res.status(404).json({ error: 'Project not found' });
      }
      
      // Get tensions
      const tensions = await sql`
        SELECT * FROM tensions 
        WHERE project_id = ${project.id} AND is_hidden = FALSE
        ORDER BY display_order
      `;
      
      // Determine round from code
      let round = null;
      if (code) {
        round = project.baseline_code === code ? 'baseline' : 'comparison';
      }
      
      return res.status(200).json({
        project: {
          id: project.id,
          name: project.name,
          sessionDate: project.session_date,
          baselineCode: project.baseline_code,
          comparisonCode: project.comparison_code
        },
        tensions: tensions.map(t => ({
          id: t.id,
          name: t.name,
          leftAim: { label: t.left_aim_label, description: t.left_aim_description },
          rightAim: { label: t.right_aim_label, description: t.right_aim_description }
        })),
        round
      });
      
    } else if (req.method === 'POST') {
      const { name, tensions } = req.body;
      
      if (!name) {
        return res.status(400).json({ error: 'Project name required' });
      }
      
      const projectId = generateId();
      const baselineCode = generateCode();
      const comparisonCode = generateCode();
      
      // Create project
      await sql`
        INSERT INTO projects (id, name, baseline_code, comparison_code)
        VALUES (${projectId}, ${name}, ${baselineCode}, ${comparisonCode})
      `;
      
      // Create tensions if provided
      if (tensions && tensions.length > 0) {
        for (let i = 0; i < tensions.length; i++) {
          const t = tensions[i];
          const tensionId = 't_' + Math.random().toString(36).substr(2, 9);
          await sql`
            INSERT INTO tensions (id, project_id, name, left_aim_label, left_aim_description, right_aim_label, right_aim_description, display_order)
            VALUES (${tensionId}, ${projectId}, ${t.name}, ${t.leftAim?.label || ''}, ${t.leftAim?.description || ''}, ${t.rightAim?.label || ''}, ${t.rightAim?.description || ''}, ${i})
          `;
        }
      }
      
      return res.status(200).json({
        project: {
          id: projectId,
          name,
          baselineCode,
          comparisonCode
        }
      });
      
    } else {
      return res.status(405).json({ error: 'Method not allowed' });
    }
    
  } catch (error) {
    console.error('Project API error:', error);
    return res.status(500).json({ error: 'Database error', details: error.message });
  }
};
