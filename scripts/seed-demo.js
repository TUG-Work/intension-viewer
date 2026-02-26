/**
 * Seed Demo Data
 * 
 * Creates the March 2025 AI Strategy session with tensions.
 * Run with: node scripts/seed-demo.js
 */

const { neon } = require('@neondatabase/serverless');

const DEMO_PROJECT = {
  id: 'demo-march-2025',
  name: 'AI Strategy Session - March 2025',
  baselineCode: 'DEMO01',
  comparisonCode: 'DEMO02'
};

const DEMO_TENSIONS = [
  {
    id: 't_quality_quantity',
    name: 'Quality vs Quantity of Outputs',
    leftAim: { label: 'Quality', description: 'Focus on excellence' },
    rightAim: { label: 'Quantity', description: 'Focus on volume' }
  },
  {
    id: 't_tracking_privacy',
    name: 'Data Tracking vs Privacy',
    leftAim: { label: 'Comprehensive Tracking', description: '' },
    rightAim: { label: 'Privacy by Design', description: '' }
  },
  {
    id: 't_oversight_personal',
    name: 'Oversight vs Personalization',
    leftAim: { label: 'Centralized Oversight', description: '' },
    rightAim: { label: 'Personalization', description: '' }
  },
  {
    id: 't_outputs_experiences',
    name: 'Outputs vs Experiences',
    leftAim: { label: 'Good AI Outputs', description: '' },
    rightAim: { label: 'Good Workflow Experiences', description: '' }
  },
  {
    id: 't_back_front',
    name: 'Back Office vs Front Office',
    leftAim: { label: 'Back Office', description: '' },
    rightAim: { label: 'Front Office', description: '' }
  },
  {
    id: 't_understanding_privacy',
    name: 'Understanding vs Privacy',
    leftAim: { label: 'Understanding', description: '' },
    rightAim: { label: 'Privacy', description: '' }
  },
  {
    id: 't_responsive_inclusive',
    name: 'Responsive vs Inclusive Governance',
    leftAim: { label: 'Quick Response', description: '' },
    rightAim: { label: 'Inclusive Process', description: '' }
  }
];

async function seed() {
  const databaseUrl = process.env.DATABASE_URL;
  
  if (!databaseUrl) {
    console.error('ERROR: DATABASE_URL environment variable is required');
    process.exit(1);
  }
  
  console.log('Connecting to database...');
  const sql = neon(databaseUrl);
  
  // Check if demo project exists
  const existing = await sql`SELECT id FROM projects WHERE id = ${DEMO_PROJECT.id}`;
  
  if (existing.length > 0) {
    console.log('Demo project already exists. Skipping...');
    console.log('');
    console.log('To re-seed, delete it first:');
    console.log(`  DELETE FROM projects WHERE id = '${DEMO_PROJECT.id}';`);
    return;
  }
  
  console.log('Creating demo project...');
  await sql`
    INSERT INTO projects (id, name, baseline_code, comparison_code)
    VALUES (${DEMO_PROJECT.id}, ${DEMO_PROJECT.name}, ${DEMO_PROJECT.baselineCode}, ${DEMO_PROJECT.comparisonCode})
  `;
  
  console.log('Creating tensions...');
  for (let i = 0; i < DEMO_TENSIONS.length; i++) {
    const t = DEMO_TENSIONS[i];
    await sql`
      INSERT INTO tensions (id, project_id, name, left_aim_label, left_aim_description, right_aim_label, right_aim_description, display_order)
      VALUES (${t.id}, ${DEMO_PROJECT.id}, ${t.name}, ${t.leftAim.label}, ${t.leftAim.description}, ${t.rightAim.label}, ${t.rightAim.description}, ${i})
    `;
  }
  
  console.log('');
  console.log('✓ Demo data seeded successfully');
  console.log('');
  console.log('Project:', DEMO_PROJECT.name);
  console.log('Baseline voting code:', DEMO_PROJECT.baselineCode);
  console.log('Comparison voting code:', DEMO_PROJECT.comparisonCode);
  console.log('');
  console.log('Tensions:', DEMO_TENSIONS.length);
  DEMO_TENSIONS.forEach((t, i) => {
    console.log(`  ${i + 1}. ${t.name}`);
  });
}

seed().catch(err => {
  console.error('Seed failed:', err.message);
  process.exit(1);
});
