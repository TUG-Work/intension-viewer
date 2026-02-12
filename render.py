"""
In/Tension Continuum Renderer

Generates HTML/SVG visualization of tension voting results.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Aim:
    label: str


@dataclass 
class Tension:
    name: str
    left_aim: Aim
    right_aim: Aim
    votes: List[int]  # Simple list of vote values for now
    
    def average(self) -> float:
        if not self.votes:
            return 5.0  # Default to center
        return sum(self.votes) / len(self.votes)


def render_continuum(tension: Tension, width: int = 800, height: int = 200) -> str:
    """Render a single continuum as SVG."""
    
    # Layout constants
    margin = 100
    bar_width = width - (margin * 2)
    bar_height = 20
    bar_y = height // 2
    positions = 11  # 0-10 scale
    slot_width = bar_width / positions
    
    # Count votes at each position
    vote_counts = [0] * positions
    for v in tension.votes:
        if 0 <= v < positions:
            vote_counts[v] += 1
    
    # Build SVG
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="#fafafa"/>
  
  <!-- Title -->
  <text x="{width//2}" y="30" text-anchor="middle" font-family="system-ui" font-size="16" font-weight="bold">{tension.name}</text>
  
  <!-- Continuum bar -->
  <rect x="{margin}" y="{bar_y}" width="{bar_width}" height="{bar_height}" fill="#e0e0e0" stroke="#999" stroke-width="1"/>
  
  <!-- Position dividers -->
'''
    
    for i in range(positions + 1):
        x = margin + (i * slot_width)
        svg += f'  <line x1="{x}" y1="{bar_y}" x2="{x}" y2="{bar_y + bar_height}" stroke="#999" stroke-width="1"/>\n'
    
    # Vote rectangles (stacked above bar)
    vote_width = slot_width * 0.8
    vote_height = 15
    
    for pos, count in enumerate(vote_counts):
        x = margin + (pos * slot_width) + (slot_width - vote_width) / 2
        for i in range(count):
            y = bar_y - (vote_height + 2) * (i + 1)
            svg += f'  <rect x="{x}" y="{y}" width="{vote_width}" height="{vote_height}" fill="#888" stroke="#666" stroke-width="1"/>\n'
    
    # Average marker
    avg = tension.average()
    avg_x = margin + (avg * slot_width) + (slot_width / 2)
    svg += f'''
  <!-- Average marker -->
  <rect x="{avg_x - 8}" y="{bar_y + 2}" width="16" height="{bar_height - 4}" fill="#333"/>
'''
    
    # Aim labels
    svg += f'''
  <!-- Aim labels -->
  <text x="{margin - 10}" y="{bar_y + bar_height//2 + 5}" text-anchor="end" font-family="system-ui" font-size="14">{tension.left_aim.label}</text>
  <text x="{margin + bar_width + 10}" y="{bar_y + bar_height//2 + 5}" text-anchor="start" font-family="system-ui" font-size="14">{tension.right_aim.label}</text>
  
</svg>'''
    
    return svg


def render_page(tensions: List[Tension]) -> str:
    """Render full HTML page with all continuums."""
    
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>In/Tension Results</title>
  <style>
    body {
      font-family: system-ui, -apple-system, sans-serif;
      max-width: 900px;
      margin: 0 auto;
      padding: 40px 20px;
      background: #f5f5f5;
    }
    h1 {
      text-align: center;
      color: #333;
    }
    .continuum {
      background: white;
      border-radius: 8px;
      padding: 20px;
      margin: 20px 0;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
  </style>
</head>
<body>
  <h1>In/Tension Session Results</h1>
'''
    
    for t in tensions:
        svg = render_continuum(t)
        html += f'  <div class="continuum">\n    {svg}\n  </div>\n'
    
    html += '''</body>
</html>'''
    
    return html


# Real session data
TENSIONS = [
    Tension("Quality vs Quantity of Outputs", 
            Aim("Quality"), Aim("Quantity"),
            [0, 1, 1, 4, 3, 5]),
    Tension("Data Tracking vs Privacy", 
            Aim("Comprehensive Tracking"), Aim("Privacy by Design"),
            [5, 9, 5, 9, 2, 5]),
    Tension("Oversight vs Personalization", 
            Aim("Centralized Oversight"), Aim("Personalization"),
            [1, 2, 8, 3, 5, 6]),
    Tension("Outputs vs Experiences", 
            Aim("Good AI Outputs"), Aim("Good Experiences"),
            [1, 3, 9, 3, 3, 4]),
    Tension("Back Office vs Front Office", 
            Aim("Back Office"), Aim("Front Office"),
            [0, 0, 2, 0, 1, 1]),
    Tension("Understanding vs Privacy", 
            Aim("Understanding"), Aim("Privacy"),
            [5, 7, 7, 6, 7, 3]),
    Tension("Responsive vs Inclusive Governance", 
            Aim("Quick Response"), Aim("Inclusive"),
            [2, 3, 7, 6, 4, 4]),
]


if __name__ == "__main__":
    html = render_page(TENSIONS)
    
    with open("public/index.html", "w") as f:
        f.write(html)
    
    print("Generated public/index.html")
