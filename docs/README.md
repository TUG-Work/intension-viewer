# In/Tension Viewer Documentation

## Overview

The In/Tension Viewer is a Python application that visualizes results from In/Tension modeling workshops. It implements the domain model defined in TUG's specification and renders interactive SVG visualizations.

## Architecture

```
intension-viewer/
├── models.py      # Domain model (pure business logic)
├── views.py       # Visualization layer (SVG/HTML rendering)
├── app.py         # Application entry point
├── public/        # Generated output
│   └── index.html
└── docs/          # Documentation
    ├── README.md
    └── object-model.md
```

### Design Principles

1. **Separation of Concerns**: Models know nothing about visualization; views only transform models into output.
2. **Spec Compliance**: All terminology matches the official TUG specification.
3. **Immutable Core**: Domain objects are dataclasses with clear responsibilities.

## Domain Model

### Controlled Vocabulary

These terms come directly from the TUG specification:

| Term | Definition |
|------|------------|
| **Project** | Container that holds a set of continuums to be worked through with participants |
| **Aim** | A strategic goal or position desirable to the organization |
| **Tension** | A set of two aims that must be balanced |
| **Continuum** | Visual presentation of a tension as a spectrum |
| **Continuum Set** | Collection of all continuums in a project |
| **Vote** | One participant's expression of how a continuum should be balanced |
| **Baseline** | First round of voting (how organization IS balancing) |
| **Comparison** | Second round of voting (how organization SHOULD balance) |
| **Consent Point** | Average of votes, or facilitator-adjusted value |
| **Participant** | Individual who votes on continuums |

### Class Reference

#### Project

Container for an In/Tension workshop session.

```python
@dataclass
class Project:
    id: str                           # Unique identifier
    name: str                         # Display name
    tensions: List[Tension]           # The continuums
    participants: List[Participant]   # Workshop attendees
    baseline_code: Optional[str]      # Access code for baseline round
    comparison_code: Optional[str]    # Access code for comparison round
```

**Key Methods:**
- `add_tension(tension)` - Add a tension to the project
- `add_participant(participant)` - Add a participant
- `get_visible_tensions()` - Get non-hidden tensions in display order
- `continuum_set` - Property returning all continuums for rendering

#### Tension

A pair of aims that must be balanced.

```python
@dataclass
class Tension:
    name: str                              # Display title
    left_aim: Aim                          # Position 0 on scale
    right_aim: Aim                         # Position 10 on scale
    votes: List[Vote]                      # All votes cast
    consent_points: List[ConsentPoint]     # Calculated or manual
    is_hidden: bool                        # Hidden from presentation
    order: int                             # Display order
```

**Key Methods:**
- `add_vote(vote)` - Record a vote
- `get_votes(round)` - Get votes for a specific round
- `get_consent_point(round)` - Get calculated or manual consent point
- `set_consent_point(round, value)` - Facilitator override
- `get_movement()` - Calculate shift between baseline and comparison
- `as_continuum()` - Get visual representation

#### Vote

One participant's expression of how a continuum should be balanced.

A Vote captures both **context** and **focus**:

```python
@dataclass
class Vote:
    # CONTEXT - Where this vote lives
    participant: Participant      # Who cast this vote
    tension_id: str              # Which continuum
    round: VotingRound           # Baseline or Comparison
    project_id: Optional[str]    # Parent project
    
    # FOCUS - The actual expression
    value: int                   # Position on scale (0-10)
    
    # LIFECYCLE
    submitted_at: Optional[str]  # When first submitted
    updated_at: Optional[str]    # When last edited
```

**Context** establishes the vote's place in the system:
- Which participant owns it
- Which tension/continuum it applies to
- Which round it belongs to
- Which project it's part of

**Focus** is the actual value being expressed:
- An integer position on the continuum scale
- Lower values lean toward the left aim
- Higher values lean toward the right aim

**Lifecycle** tracks when the vote was cast and modified:
- Per spec: "Participants must be able to return to continuums and edit votes when this function has been enabled by the facilitator."

#### Aim

A strategic goal or position.

```python
@dataclass
class Aim:
    label: str                    # Short name (e.g., "Quality")
    description: Optional[str]    # Longer explanation
```

#### Participant

An individual who votes on continuums.

```python
@dataclass
class Participant:
    id: str                       # Unique identifier
    display_name: str             # Shown in results
    color: Optional[str]          # Visual distinction
```

#### ConsentPoint

The agreed-upon position after discussion.

```python
@dataclass
class ConsentPoint:
    round: VotingRound           # Which round
    value: float                 # Position (can be fractional)
    is_manual: bool              # True if facilitator adjusted
```

**Key Behavior:**
- Defaults to calculated average of all votes
- Facilitator can override to capture group consensus
- `from_votes(votes, round)` class method calculates from votes

#### VotingRound

Enumeration of the two voting phases.

```python
class VotingRound(Enum):
    BASELINE = "baseline"      # How we ARE balancing
    COMPARISON = "comparison"  # How we SHOULD balance
```

#### Continuum

Visual representation of a Tension.

```python
@dataclass
class Continuum:
    tension: Tension             # The underlying tension
    scale_min: int = 0          # Left end of scale
    scale_max: int = 10         # Right end of scale
```

**Properties:**
- `scale_positions` - Number of discrete positions (11 for 0-10)

## Views

### ContinuumView

Renders a single Continuum as SVG.

**Visual Elements:**
- Solid horizontal line (the spectrum)
- Triangle fulcrum at center (balance point)
- Vote rectangles stacked above/below the line
- Consent point as circle on the line
- Aim labels at left and right ends

**Usage:**
```python
from views import ContinuumView

view = ContinuumView(continuum, show_comparison=False)
svg = view.render()
```

### ProjectView

Renders a complete Project as an HTML page.

**Sections:**
- Header with project name and stats
- All continuums in order
- Summary table with consent points

**Usage:**
```python
from views import ProjectView

view = ProjectView(project, show_comparison=False)
html = view.render()
```

## Usage Examples

### Loading Session Data

```python
from models import Project, Tension, Aim, Participant, Vote, VotingRound

# Create project
project = Project(id="workshop-2025", name="AI Strategy Workshop")

# Add participants
alice = Participant(id="alice", display_name="Alice")
project.add_participant(alice)

# Create tension
tension = Tension(
    name="Quality vs Quantity",
    left_aim=Aim(label="Quality"),
    right_aim=Aim(label="Quantity")
)
project.add_tension(tension)

# Add votes
tension.add_vote(Vote(
    participant=alice,
    tension_id=tension.name,
    round=VotingRound.BASELINE,
    project_id=project.id,
    value=3,
    submitted_at="2025-03-28T12:00:00Z"
))
```

### Generating Visualization

```python
from views import ProjectView

view = ProjectView(project)
html = view.render()

with open("output.html", "w") as f:
    f.write(html)
```

### Facilitator Override

```python
# After discussion, facilitator adjusts consent point
tension.set_consent_point(VotingRound.BASELINE, 3.5)

# Check if manual
cp = tension.get_consent_point(VotingRound.BASELINE)
print(f"Value: {cp.value}, Manual: {cp.is_manual}")
```

## Running the Application

```bash
cd /Users/kevin/Projects/intension-viewer
python3 app.py
```

This generates `public/index.html` with the visualization.

## Deployment

The `public/` directory can be deployed to any static hosting:

1. **Vercel**: Connect GitHub repo, deploy from `public/`
2. **Local**: `open public/index.html`

## Future Extensions

- Comparison round visualization (votes below the line)
- Movement arrows showing shift between rounds
- PDF report generation
- CSV data export
- Real-time WebSocket updates during live workshops
