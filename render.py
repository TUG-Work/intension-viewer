"""
In/Tension Continuum Renderer

Generates HTML/SVG visualization matching TUG's wireframe design.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Aim:
    label: str
    description: Optional[str] = None


@dataclass 
class Tension:
    name: str
    left_aim: Aim
    right_aim: Aim
    baseline_votes: List[int]
    comparison_votes: Optional[List[int]] = None
    
    def baseline_average(self) -> Optional[float]:
        if not self.baseline_votes:
            return None
        return sum(self.baseline_votes) / len(self.baseline_votes)
    
    def comparison_average(self) -> Optional[float]:
        if not self.comparison_votes:
            return None
        return sum(self.comparison_votes) / len(self.comparison_votes)
    
    def movement(self) -> Optional[float]:
        b, c = self.baseline_average(), self.comparison_average()
        if b is None or c is None:
            return None
        return c - b


def render_continuum(tension: Tension, 
                     width: int = 900, 
                     height: int = 280,
                     show_comparison: bool = False) -> str:
    """
    Render a single continuum as SVG.
    
    Design based on TUG wireframes:
    - Clean white background with subtle border
    - Discrete cells for each position (0-10)
    - Vote rectangles stack above (baseline) and below (comparison)
    - Average marker sits on the bar
    - Bold aim labels at ends
    """
    
    # Layout
    margin_x = 140
    bar_width = width - (margin_x * 2)
    bar_height = 32
    bar_y = height // 2
    positions = 11  # 0-10 scale
    cell_width = bar_width / positions
    
    # Vote display
    vote_width = cell_width * 0.7
    vote_height = 18
    vote_gap = 3
    
    # Colors (matching wireframe aesthetic)
    colors = {
        'background': '#ffffff',
        'border': '#e0e0e0',
        'bar_fill': '#ffffff',
        'bar_stroke': '#999999',
        'baseline_vote': '#a8d4f0',  # Light blue
        'baseline_avg': '#666666',
        'comparison_vote': '#404040',
        'comparison_avg': '#1a1a1a',
        'text': '#333333',
        'text_light': '#666666',
    }
    
    # Count votes at each position
    baseline_counts = [0] * positions
    for v in tension.baseline_votes:
        if 0 <= v < positions:
            baseline_counts[v] += 1
    
    comparison_counts = [0] * positions
    if tension.comparison_votes:
        for v in tension.comparison_votes:
            if 0 <= v < positions:
                comparison_counts[v] += 1
    
    # Start SVG
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="{colors['background']}" stroke="{colors['border']}" stroke-width="1"/>
  
  <!-- Title -->
  <text x="40" y="40" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="600" fill="{colors['text']}">{tension.name}</text>
'''
    
    # Legend
    legend_y = 40
    if show_comparison and tension.comparison_votes:
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
    
    # Continuum bar (solid line)
    line_y = bar_y + bar_height // 2
    svg += f'''
  <!-- Continuum line -->
  <line x1="{margin_x}" y1="{line_y}" x2="{margin_x + bar_width}" y2="{line_y}" stroke="{colors['bar_stroke']}" stroke-width="3"/>
  
  <!-- Center fulcrum triangle -->
  <polygon points="{width//2},{line_y + 8} {width//2 - 20},{line_y + 40} {width//2 + 20},{line_y + 40}" fill="{colors['text']}" />
'''
    
    # Baseline vote rectangles (above bar)
    for pos, count in enumerate(baseline_counts):
        if count == 0:
            continue
        cell_center = margin_x + (pos * cell_width) + (cell_width / 2)
        x = cell_center - (vote_width / 2)
        for i in range(count):
            y = bar_y - (vote_height + vote_gap) * (i + 1)
            svg += f'  <rect x="{x:.1f}" y="{y:.1f}" width="{vote_width:.1f}" height="{vote_height}" fill="{colors["baseline_vote"]}" rx="2"/>\n'
    
    # Comparison vote rectangles (below bar)
    if show_comparison and tension.comparison_votes:
        for pos, count in enumerate(comparison_counts):
            if count == 0:
                continue
            cell_center = margin_x + (pos * cell_width) + (cell_width / 2)
            x = cell_center - (vote_width / 2)
            for i in range(count):
                y = bar_y + bar_height + vote_gap + (vote_height + vote_gap) * i
                svg += f'  <rect x="{x:.1f}" y="{y:.1f}" width="{vote_width:.1f}" height="{vote_height}" fill="{colors["comparison_vote"]}" rx="2"/>\n'
    
    # Baseline average marker (circle on line)
    line_y = bar_y + bar_height // 2
    baseline_avg = tension.baseline_average()
    if baseline_avg is not None:
        avg_x = margin_x + (baseline_avg * cell_width) + (cell_width / 2)
        svg += f'''
  <!-- Baseline average -->
  <circle cx="{avg_x:.1f}" cy="{line_y}" r="12" fill="{colors['baseline_avg']}" stroke="#fff" stroke-width="2"/>
'''
    
    # Comparison average marker (circle, different style)
    if show_comparison and tension.comparison_votes:
        comp_avg = tension.comparison_average()
        if comp_avg is not None:
            avg_x = margin_x + (comp_avg * cell_width) + (cell_width / 2)
            svg += f'''
  <!-- Comparison average -->
  <circle cx="{avg_x:.1f}" cy="{line_y}" r="12" fill="{colors['comparison_avg']}" stroke="#fff" stroke-width="2"/>
'''
    
    # Aim labels (stacked if long)
    def wrap_label(label, max_chars=18):
        """Split label into lines if too long."""
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
    
    # Left aim
    left_lines = wrap_label(tension.left_aim.label)
    line_height = 18
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

    
    # Aim descriptions (if provided)
    if tension.left_aim.description:
        svg += f'  <text x="{margin_x - 20}" y="{bar_y + bar_height/2 + 24}" text-anchor="end" font-family="system-ui" font-size="11" fill="{colors["text_light"]}">{tension.left_aim.description}</text>\n'
    if tension.right_aim.description:
        svg += f'  <text x="{margin_x + bar_width + 20}" y="{bar_y + bar_height/2 + 24}" text-anchor="start" font-family="system-ui" font-size="11" fill="{colors["text_light"]}">{tension.right_aim.description}</text>\n'
    
    svg += '</svg>'
    return svg


def render_page(tensions: List[Tension], title: str = "In/Tension Session Results") -> str:
    """Render full HTML page with all continuums."""
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    * {{
      box-sizing: border-box;
    }}
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      max-width: 960px;
      margin: 0 auto;
      padding: 48px 24px;
      background: #f0f0f0;
      color: #333;
    }}
    header {{
      text-align: center;
      margin-bottom: 48px;
    }}
    h1 {{
      font-size: 28px;
      font-weight: 600;
      margin: 0 0 8px 0;
    }}
    .subtitle {{
      color: #666;
      font-size: 14px;
    }}
    .continuum {{
      margin: 24px 0;
    }}
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
    .stats h2 {{
      font-size: 16px;
      margin: 0 0 16px 0;
    }}
    .stats table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    .stats th, .stats td {{
      text-align: left;
      padding: 8px 12px;
      border-bottom: 1px solid #eee;
    }}
    .stats th {{
      font-weight: 500;
      color: #666;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{title}</h1>
    <p class="subtitle">6 participants · 7 tensions · Baseline round</p>
  </header>
'''
    
    for t in tensions:
        svg = render_continuum(t)
        html += f'  <div class="continuum">\n    {svg}\n  </div>\n'
    
    # Summary stats
    html += '''
  <div class="stats">
    <h2>Summary</h2>
    <table>
      <tr>
        <th>Tension</th>
        <th>Average</th>
        <th>Leans Toward</th>
      </tr>
'''
    
    for t in tensions:
        avg = t.baseline_average()
        if avg is not None:
            if avg < 4:
                leans = t.left_aim.label
            elif avg > 6:
                leans = t.right_aim.label
            else:
                leans = "Center"
            html += f'      <tr><td>{t.name}</td><td>{avg:.1f}</td><td>{leans}</td></tr>\n'
    
    html += '''    </table>
  </div>
</body>
</html>'''
    
    return html


# Real session data (March 2025)
TENSIONS = [
    Tension(
        "Quality vs Quantity of Outputs",
        Aim("Quality", "Focus on excellence"),
        Aim("Quantity", "Focus on volume"),
        baseline_votes=[0, 1, 1, 4, 3, 5]
    ),
    Tension(
        "Data Tracking vs Privacy",
        Aim("Comprehensive Tracking"),
        Aim("Privacy by Design"),
        baseline_votes=[5, 9, 5, 9, 2, 5]
    ),
    Tension(
        "Oversight vs Personalization",
        Aim("Centralized Oversight"),
        Aim("Personalization"),
        baseline_votes=[1, 2, 8, 3, 5, 6]
    ),
    Tension(
        "Outputs vs Experiences",
        Aim("Good AI Outputs"),
        Aim("Good Workflow Experiences"),
        baseline_votes=[1, 3, 9, 3, 3, 4]
    ),
    Tension(
        "Back Office vs Front Office",
        Aim("Back Office"),
        Aim("Front Office"),
        baseline_votes=[0, 0, 2, 0, 1, 1]
    ),
    Tension(
        "Understanding vs Privacy",
        Aim("Understanding"),
        Aim("Privacy"),
        baseline_votes=[5, 7, 7, 6, 7, 3]
    ),
    Tension(
        "Responsive vs Inclusive Governance",
        Aim("Quick Response"),
        Aim("Inclusive Process"),
        baseline_votes=[2, 3, 7, 6, 4, 4]
    ),
]


if __name__ == "__main__":
    html = render_page(TENSIONS)
    
    with open("public/index.html", "w") as f:
        f.write(html)
    
    print("Generated public/index.html")
