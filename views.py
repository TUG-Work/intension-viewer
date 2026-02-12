"""
In/Tension Views

SVG and HTML rendering for the domain model.
Transforms model objects into visual representations.
"""

from models import (
    Project, Tension, Continuum, VotingRound
)
from typing import List


class ContinuumView:
    """
    Renders a Continuum as SVG.
    
    Visual elements:
    - Solid horizontal line (the spectrum)
    - Triangle fulcrum at center (balance point)
    - Vote rectangles stacked above/below the line
    - Consent point as circle on the line
    - Aim labels at left and right ends
    """
    
    # Default dimensions
    WIDTH = 900
    HEIGHT = 280
    MARGIN_X = 140
    
    # Colors
    COLORS = {
        'background': '#ffffff',
        'border': '#e0e0e0',
        'line': '#999999',
        'fulcrum': '#333333',
        'baseline_vote': '#a8d4f0',
        'baseline_consent': '#666666',
        'comparison_vote': '#404040',
        'comparison_consent': '#1a1a1a',
        'text': '#333333',
        'text_light': '#666666',
    }
    
    def __init__(self, continuum: Continuum, show_comparison: bool = False):
        self.continuum = continuum
        self.tension = continuum.tension
        self.show_comparison = show_comparison
        
        # Calculated layout
        self.bar_width = self.WIDTH - (self.MARGIN_X * 2)
        self.bar_y = self.HEIGHT // 2
        self.line_y = self.bar_y + 16
        self.positions = continuum.scale_positions
        self.cell_width = self.bar_width / self.positions
        
        # Vote dimensions
        self.vote_width = self.cell_width * 0.7
        self.vote_height = 18
        self.vote_gap = 3
    
    def render(self) -> str:
        """Generate complete SVG for this continuum."""
        parts = [
            self._svg_open(),
            self._background(),
            self._title(),
            self._legend(),
            self._line_and_fulcrum(),
            self._baseline_votes(),
            self._comparison_votes() if self.show_comparison else '',
            self._baseline_consent_point(),
            self._comparison_consent_point() if self.show_comparison else '',
            self._aim_labels(),
            self._svg_close(),
        ]
        return '\n'.join(parts)
    
    def _svg_open(self) -> str:
        return f'<svg width="{self.WIDTH}" height="{self.HEIGHT}" xmlns="http://www.w3.org/2000/svg">'
    
    def _svg_close(self) -> str:
        return '</svg>'
    
    def _background(self) -> str:
        return f'''  <rect width="{self.WIDTH}" height="{self.HEIGHT}" 
        fill="{self.COLORS['background']}" 
        stroke="{self.COLORS['border']}" stroke-width="1"/>'''
    
    def _title(self) -> str:
        return f'''  <text x="40" y="40" 
        font-family="system-ui, -apple-system, sans-serif" 
        font-size="18" font-weight="600" 
        fill="{self.COLORS['text']}">{self.tension.name}</text>'''
    
    def _legend(self) -> str:
        x = self.WIDTH - 200 if self.show_comparison else self.WIDTH - 160
        y = 40
        
        svg = f'''  <rect x="{x}" y="{y - 12}" width="16" height="12" fill="{self.COLORS['baseline_vote']}"/>
  <text x="{x + 20}" y="{y}" font-family="system-ui" font-size="12" fill="{self.COLORS['text_light']}">Baseline votes</text>'''
        
        if self.show_comparison:
            svg += f'''
  <rect x="{x}" y="{y + 8}" width="16" height="12" fill="{self.COLORS['comparison_vote']}"/>
  <text x="{x + 20}" y="{y + 20}" font-family="system-ui" font-size="12" fill="{self.COLORS['text_light']}">Comparison votes</text>'''
        
        return svg
    
    def _line_and_fulcrum(self) -> str:
        center_x = self.WIDTH // 2
        return f'''  <!-- Continuum line -->
  <line x1="{self.MARGIN_X}" y1="{self.line_y}" 
        x2="{self.MARGIN_X + self.bar_width}" y2="{self.line_y}" 
        stroke="{self.COLORS['line']}" stroke-width="3"/>
  
  <!-- Fulcrum triangle -->
  <polygon points="{center_x},{self.line_y + 8} {center_x - 20},{self.line_y + 40} {center_x + 20},{self.line_y + 40}" 
           fill="{self.COLORS['fulcrum']}"/>'''
    
    def _count_votes_by_position(self, round: VotingRound) -> List[int]:
        """Count how many votes landed at each position."""
        counts = [0] * self.positions
        for vote in self.tension.get_votes(round):
            pos = vote.value - self.continuum.scale_min
            if 0 <= pos < self.positions:
                counts[pos] += 1
        return counts
    
    def _render_vote_stack(self, counts: List[int], above: bool, color: str) -> str:
        """Render stacked vote rectangles."""
        svg_parts = []
        
        for pos, count in enumerate(counts):
            if count == 0:
                continue
            
            cell_center = self.MARGIN_X + (pos * self.cell_width) + (self.cell_width / 2)
            x = cell_center - (self.vote_width / 2)
            
            for i in range(count):
                if above:
                    y = self.line_y - 8 - (self.vote_height + self.vote_gap) * (i + 1)
                else:
                    y = self.line_y + 8 + self.vote_gap + (self.vote_height + self.vote_gap) * i
                
                svg_parts.append(
                    f'  <rect x="{x:.1f}" y="{y:.1f}" '
                    f'width="{self.vote_width:.1f}" height="{self.vote_height}" '
                    f'fill="{color}" rx="2"/>'
                )
        
        return '\n'.join(svg_parts)
    
    def _baseline_votes(self) -> str:
        counts = self._count_votes_by_position(VotingRound.BASELINE)
        return self._render_vote_stack(counts, above=True, color=self.COLORS['baseline_vote'])
    
    def _comparison_votes(self) -> str:
        counts = self._count_votes_by_position(VotingRound.COMPARISON)
        return self._render_vote_stack(counts, above=False, color=self.COLORS['comparison_vote'])
    
    def _render_consent_point(self, round: VotingRound, color: str) -> str:
        """Render consent point as circle on the line."""
        cp = self.tension.get_consent_point(round)
        if not cp:
            return ''
        
        x = self.MARGIN_X + (cp.value * self.cell_width) + (self.cell_width / 2)
        return f'''  <circle cx="{x:.1f}" cy="{self.line_y}" r="12" 
          fill="{color}" stroke="#fff" stroke-width="2"/>'''
    
    def _baseline_consent_point(self) -> str:
        return self._render_consent_point(VotingRound.BASELINE, self.COLORS['baseline_consent'])
    
    def _comparison_consent_point(self) -> str:
        return self._render_consent_point(VotingRound.COMPARISON, self.COLORS['comparison_consent'])
    
    def _wrap_label(self, label: str, max_chars: int = 18) -> List[str]:
        """Split label into multiple lines if too long."""
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
    
    def _aim_labels(self) -> str:
        """Render aim labels, stacked if long."""
        line_height = 18
        svg_parts = []
        
        # Left aim
        left_lines = self._wrap_label(self.tension.left_aim.label)
        start_y = self.line_y - (len(left_lines) - 1) * line_height / 2
        
        for i, line in enumerate(left_lines):
            y = start_y + i * line_height
            svg_parts.append(
                f'  <text x="{self.MARGIN_X - 20}" y="{y}" text-anchor="end" '
                f'font-family="system-ui, -apple-system, sans-serif" '
                f'font-size="15" font-weight="600" fill="{self.COLORS["text"]}">{line}</text>'
            )
        
        # Right aim
        right_lines = self._wrap_label(self.tension.right_aim.label)
        start_y = self.line_y - (len(right_lines) - 1) * line_height / 2
        
        for i, line in enumerate(right_lines):
            y = start_y + i * line_height
            svg_parts.append(
                f'  <text x="{self.MARGIN_X + self.bar_width + 20}" y="{y}" text-anchor="start" '
                f'font-family="system-ui, -apple-system, sans-serif" '
                f'font-size="15" font-weight="600" fill="{self.COLORS["text"]}">{line}</text>'
            )
        
        return '\n'.join(svg_parts)


class ProjectView:
    """
    Renders a Project as an HTML page with all continuums.
    """
    
    def __init__(self, project: Project, show_comparison: bool = False):
        self.project = project
        self.show_comparison = show_comparison
    
    def render(self) -> str:
        """Generate complete HTML page."""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{self.project.name}</title>
  {self._styles()}
</head>
<body>
  {self._header()}
  {self._continuums()}
  {self._summary()}
</body>
</html>'''
    
    def _styles(self) -> str:
        return '''<style>
    * { box-sizing: border-box; }
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      max-width: 960px;
      margin: 0 auto;
      padding: 48px 24px;
      background: #f0f0f0;
      color: #333;
    }
    header { text-align: center; margin-bottom: 48px; }
    h1 { font-size: 28px; font-weight: 600; margin: 0 0 8px 0; }
    .subtitle { color: #666; font-size: 14px; }
    .continuum { margin: 24px 0; }
    .continuum svg {
      display: block;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
      border-radius: 4px;
    }
    .stats {
      margin-top: 48px;
      padding: 24px;
      background: white;
      border-radius: 4px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .stats h2 { font-size: 16px; margin: 0 0 16px 0; }
    .stats table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .stats th, .stats td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #eee; }
    .stats th { font-weight: 500; color: #666; }
  </style>'''
    
    def _header(self) -> str:
        p_count = len(self.project.participants)
        t_count = len(self.project.get_visible_tensions())
        round_text = "Baseline + Comparison" if self.show_comparison else "Baseline round"
        
        return f'''<header>
    <h1>{self.project.name}</h1>
    <p class="subtitle">{p_count} participants · {t_count} tensions · {round_text}</p>
  </header>'''
    
    def _continuums(self) -> str:
        parts = []
        for continuum in self.project.continuum_set:
            view = ContinuumView(continuum, show_comparison=self.show_comparison)
            parts.append(f'  <div class="continuum">\n    {view.render()}\n  </div>')
        return '\n'.join(parts)
    
    def _summary(self) -> str:
        rows = []
        for tension in self.project.get_visible_tensions():
            cp = tension.get_consent_point(VotingRound.BASELINE)
            if cp:
                if cp.value < 4:
                    leans = tension.left_aim.label
                elif cp.value > 6:
                    leans = tension.right_aim.label
                else:
                    leans = "Center"
                manual = " (adjusted)" if cp.is_manual else ""
                rows.append(f'<tr><td>{tension.name}</td><td>{cp.value:.1f}{manual}</td><td>{leans}</td></tr>')
        
        return f'''<div class="stats">
    <h2>Summary</h2>
    <table>
      <tr><th>Tension</th><th>Consent Point</th><th>Leans Toward</th></tr>
      {''.join(rows)}
    </table>
  </div>'''
