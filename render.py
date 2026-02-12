"""
In/Tension Continuum Renderer

Generates HTML/SVG visualization from the domain model.
"""

from models import (
    Project, Tension, Aim, Participant, Vote, 
    VotingRound, Continuum, ConsentPoint
)
from typing import List


def render_continuum(continuum: Continuum, 
                     width: int = 900, 
                     height: int = 280,
                     show_comparison: bool = False) -> str:
    """
    Render a Continuum as SVG.
    
    Visual design:
    - Solid horizontal line with triangle fulcrum at center
    - Vote rectangles stack above (baseline) and below (comparison)
    - Consent point shown as circle on the line
    - Aim labels at ends, stacked if long
    """
    
    tension = continuum.tension
    positions = continuum.scale_positions
    
    # Layout
    margin_x = 140
    bar_width = width - (margin_x * 2)
    bar_height = 32
    bar_y = height // 2
    cell_width = bar_width / positions
    
    # Vote display
    vote_width = cell_width * 0.7
    vote_height = 18
    vote_gap = 3
    
    # Colors
    colors = {
        'background': '#ffffff',
        'border': '#e0e0e0',
        'bar_stroke': '#999999',
        'baseline_vote': '#a8d4f0',  # Light blue
        'baseline_avg': '#666666',
        'comparison_vote': '#404040',
        'comparison_avg': '#1a1a1a',
        'text': '#333333',
        'text_light': '#666666',
        'fulcrum': '#333333',
    }
    
    # Count votes at each position
    baseline_votes = tension.get_votes(VotingRound.BASELINE)
    baseline_counts = [0] * positions
    for v in baseline_votes:
        if continuum.scale_min <= v.value <= continuum.scale_max:
            baseline_counts[v.value - continuum.scale_min] += 1
    
    comparison_votes = tension.get_votes(VotingRound.COMPARISON)
    comparison_counts = [0] * positions
    for v in comparison_votes:
        if continuum.scale_min <= v.value <= continuum.scale_max:
            comparison_counts[v.value - continuum.scale_min] += 1
    
    line_y = bar_y + bar_height // 2
    
    # Start SVG
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="{colors['background']}" stroke="{colors['border']}" stroke-width="1"/>
  
  <!-- Title -->
  <text x="40" y="40" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="600" fill="{colors['text']}">{tension.name}</text>
'''
    
    # Legend
    legend_y = 40
    if show_comparison and comparison_votes:
        svg += f'''
  <!-- Legend -->
  <rect x="{width - 200}" y="{legend_y - 12}" width="16" height="12" fill="{colors['baseline_vote']}"/>
  <text x="{width - 180}" y="{legend_y}" font-family="system-ui" font-size="12" fill="{colors['text_light']}">Baseline votes</text>
  <rect x="{width - 200}" y="{legend_y + 8}" width="16" height="12" fill="{colors['comparison_vote']}"/>
  <text x="{width - 180}" y="{legend_y + 20}" font-family="system-ui" font-size="12" fill="{colors['text_light']}">Comparison votes</text>
'''
    else:
        svg += f'''
  <!-- Legend -->
  <rect x="{width - 160}" y="{legend_y - 12}" width="16" height="12" fill="{colors['baseline_vote']}"/>
  <text x="{width - 140}" y="{legend_y}" font-family="system-ui" font-size="12" fill="{colors['text_light']}">Baseline votes</text>
'''
    
    # Continuum line and fulcrum
    svg += f'''
  <!-- Continuum line -->
  <line x1="{margin_x}" y1="{line_y}" x2="{margin_x + bar_width}" y2="{line_y}" stroke="{colors['bar_stroke']}" stroke-width="3"/>
  
  <!-- Center fulcrum triangle -->
  <polygon points="{width//2},{line_y + 8} {width//2 - 20},{line_y + 40} {width//2 + 20},{line_y + 40}" fill="{colors['fulcrum']}" />
'''
    
    # Baseline vote rectangles (above line)
    for pos, count in enumerate(baseline_counts):
        if count == 0:
            continue
        cell_center = margin_x + (pos * cell_width) + (cell_width / 2)
        x = cell_center - (vote_width / 2)
        for i in range(count):
            y = line_y - 8 - (vote_height + vote_gap) * (i + 1)
            svg += f'  <rect x="{x:.1f}" y="{y:.1f}" width="{vote_width:.1f}" height="{vote_height}" fill="{colors["baseline_vote"]}" rx="2"/>\n'
    
    # Comparison vote rectangles (below line)
    if show_comparison and comparison_votes:
        for pos, count in enumerate(comparison_counts):
            if count == 0:
                continue
            cell_center = margin_x + (pos * cell_width) + (cell_width / 2)
            x = cell_center - (vote_width / 2)
            for i in range(count):
                y = line_y + 8 + vote_gap + (vote_height + vote_gap) * i
                svg += f'  <rect x="{x:.1f}" y="{y:.1f}" width="{vote_width:.1f}" height="{vote_height}" fill="{colors["comparison_vote"]}" rx="2"/>\n'
    
    # Baseline consent point (circle on line)
    baseline_cp = tension.get_consent_point(VotingRound.BASELINE)
    if baseline_cp:
        cp_x = margin_x + (baseline_cp.value * cell_width) + (cell_width / 2)
        svg += f'''
  <!-- Baseline consent point -->
  <circle cx="{cp_x:.1f}" cy="{line_y}" r="12" fill="{colors['baseline_avg']}" stroke="#fff" stroke-width="2"/>
'''
    
    # Comparison consent point
    if show_comparison and comparison_votes:
        comparison_cp = tension.get_consent_point(VotingRound.COMPARISON)
        if comparison_cp:
            cp_x = margin_x + (comparison_cp.value * cell_width) + (cell_width / 2)
            svg += f'''
  <!-- Comparison consent point -->
  <circle cx="{cp_x:.1f}" cy="{line_y}" r="12" fill="{colors['comparison_avg']}" stroke="#fff" stroke-width="2"/>
'''
    
    # Aim labels (stacked if long)
    def wrap_label(label, max_chars=18):
        words = label.split()
        lines = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 <= max_chars:
                current = f"{current} {word}".strip()
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines if lines else [label]
    
    line_height = 18
    
    # Left aim
    left_lines = wrap_label(tension.left_aim.label)
    start_y = bar_y + bar_height/2 - (len(left_lines) - 1) * line_height / 2
    svg += '  <!-- Left aim label -->\n'
    for i, line in enumerate(left_lines):
        y = start_y + i * line_height
        svg += f'  <text x="{margin_x - 20}" y="{y}" text-anchor="end" font-family="system-ui, -apple-system, sans-serif" font-size="15" font-weight="600" fill="{colors["text"]}">{line}</text>\n'
    
    # Right aim
    right_lines = wrap_label(tension.right_aim.label)
    start_y = bar_y + bar_height/2 - (len(right_lines) - 1) * line_height / 2
    svg += '  <!-- Right aim label -->\n'
    for i, line in enumerate(right_lines):
        y = start_y + i * line_height
        svg += f'  <text x="{margin_x + bar_width + 20}" y="{y}" text-anchor="start" font-family="system-ui, -apple-system, sans-serif" font-size="15" font-weight="600" fill="{colors["text"]}">{line}</text>\n'

    svg += '</svg>'
    return svg


def render_project(project: Project, show_comparison: bool = False) -> str:
    """Render full HTML page for a project's continuum set."""
    
    participant_count = len(project.participants)
    tension_count = len(project.get_visible_tensions())
    round_text = "Baseline + Comparison" if show_comparison else "Baseline round"
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{project.name}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      max-width: 960px;
      margin: 0 auto;
      padding: 48px 24px;
      background: #f0f0f0;
      color: #333;
    }}
    header {{ text-align: center; margin-bottom: 48px; }}
    h1 {{ font-size: 28px; font-weight: 600; margin: 0 0 8px 0; }}
    .subtitle {{ color: #666; font-size: 14px; }}
    .continuum {{ margin: 24px 0; }}
    .continuum svg {{
      display: block;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
      border-radius: 4px;
    }}
    .stats {{
      margin-top: 48px;
      padding: 24px;
      background: white;
      border-radius: 4px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }}
    .stats h2 {{ font-size: 16px; margin: 0 0 16px 0; }}
    .stats table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    .stats th, .stats td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid #eee; }}
    .stats th {{ font-weight: 500; color: #666; }}
  </style>
</head>
<body>
  <header>
    <h1>{project.name}</h1>
    <p class="subtitle">{participant_count} participants · {tension_count} tensions · {round_text}</p>
  </header>
'''
    
    for continuum in project.continuum_set:
        svg = render_continuum(continuum, show_comparison=show_comparison)
        html += f'  <div class="continuum">\n    {svg}\n  </div>\n'
    
    # Summary stats
    html += '''
  <div class="stats">
    <h2>Summary</h2>
    <table>
      <tr>
        <th>Tension</th>
        <th>Consent Point</th>
        <th>Leans Toward</th>
      </tr>
'''
    
    for tension in project.get_visible_tensions():
        cp = tension.get_consent_point(VotingRound.BASELINE)
        if cp:
            if cp.value < 4:
                leans = tension.left_aim.label
            elif cp.value > 6:
                leans = tension.right_aim.label
            else:
                leans = "Center"
            manual = " (adjusted)" if cp.is_manual else ""
            html += f'      <tr><td>{tension.name}</td><td>{cp.value:.1f}{manual}</td><td>{leans}</td></tr>\n'
    
    html += '''    </table>
  </div>
</body>
</html>'''
    
    return html


def load_march_2025_session() -> Project:
    """Load the real March 2025 workshop session data."""
    
    project = Project(
        id="march-2025",
        name="In/Tension Session Results"
    )
    
    # Participants
    participants = [
        Participant(id="stratton", display_name="Stratton Glaze"),
        Participant(id="emily", display_name="Emily"),
        Participant(id="klyn", display_name="Klyn"),
        Participant(id="andrew", display_name="Andrew"),
        Participant(id="bob", display_name="Bob"),
        Participant(id="dan", display_name="Dan Heck"),
    ]
    for p in participants:
        project.add_participant(p)
    
    # Tensions with votes
    tension_data = [
        ("Quality vs Quantity of Outputs",
         Aim("Quality", "Focus on excellence"),
         Aim("Quantity", "Focus on volume"),
         [0, 1, 1, 4, 3, 5]),
        
        ("Data Tracking vs Privacy",
         Aim("Comprehensive Tracking"),
         Aim("Privacy by Design"),
         [5, 9, 5, 9, 2, 5]),
        
        ("Oversight vs Personalization",
         Aim("Centralized Oversight"),
         Aim("Personalization"),
         [1, 2, 8, 3, 5, 6]),
        
        ("Outputs vs Experiences",
         Aim("Good AI Outputs"),
         Aim("Good Workflow Experiences"),
         [1, 3, 9, 3, 3, 4]),
        
        ("Back Office vs Front Office",
         Aim("Back Office"),
         Aim("Front Office"),
         [0, 0, 2, 0, 1, 1]),
        
        ("Understanding vs Privacy",
         Aim("Understanding"),
         Aim("Privacy"),
         [5, 7, 7, 6, 7, 3]),
        
        ("Responsive vs Inclusive Governance",
         Aim("Quick Response"),
         Aim("Inclusive Process"),
         [2, 3, 7, 6, 4, 4]),
    ]
    
    for name, left_aim, right_aim, votes in tension_data:
        tension = Tension(name=name, left_aim=left_aim, right_aim=right_aim)
        for participant, value in zip(participants, votes):
            tension.add_vote(Vote(
                participant=participant,
                round=VotingRound.BASELINE,
                value=value
            ))
        project.add_tension(tension)
    
    return project


if __name__ == "__main__":
    project = load_march_2025_session()
    html = render_project(project)
    
    with open("public/index.html", "w") as f:
        f.write(html)
    
    print(f"Generated public/index.html")
    print(f"  Project: {project.name}")
    print(f"  Participants: {len(project.participants)}")
    print(f"  Tensions: {len(project.tensions)}")
