# Voting Interface — Mini Program Charter

## Why (Purpose)

Enable participants to cast votes in an In/Tension modeling workshop or exercise. The voting mechanism must be:

- **Easy** — minimal friction to express a position
- **Device-agnostic** — works on laptop, phone, tablet
- **Extensible** — components can be customized (e.g., custom vote icons, branded themes)
- **Future-proof** — architecture accommodates physical voting devices later

## What (Scope)

### Core Functionality

A participant who is authorized to vote:
1. Is presented a **sequence of Tensions**
2. For each Tension, sees **two Aims** (left and right)
3. Selects a **position on the scale**: -5 to +5 (11 increments, 0 = center)
4. Can **navigate** between tensions (back/forward)
5. **Submits** votes when complete

### Scale Structure

```
Left Aim                                              Right Aim
   |                                                      |
   ●────●────●────●────●────●────●────●────●────●────●
   0    1    2    3    4    5    6    7    8    9   10
                            ↑
                     (center, not shown)
```

User sees **11 dots only** — no numbers. Internal storage: 0-10 integer.
Visual position communicates meaning: left aim ← → right aim.

### Input Modalities

| Device | Primary Input | Secondary Input |
|--------|---------------|-----------------|
| Desktop | Click on position | Keyboard (arrow keys, numbers) |
| Tablet | Tap on position | Drag slider |
| Phone | Tap on position | Drag slider |
| Future: Physical | Hardware dial/slider | Buttons |

### Display Adaptations

| Context | Layout |
|---------|--------|
| Desktop (wide) | Horizontal scale, aims on sides |
| Mobile (narrow) | Vertical scale, aims top/bottom, OR horizontal with scrollable labels |

## Who (Actors)

**Participant** — An individual authorized to vote
- Has been invited to a session (via code or link)
- Authenticated (email or anonymous with code)
- Has voting rights for this round (baseline or comparison)

**Session** — The voting context
- Knows which Tensions are available
- Knows which Round is active
- Tracks vote status per participant

---

## Object-Oriented Architecture

### Principle: Separation of Concerns

```
┌─────────────────────────────────────────────────────────┐
│                    DOMAIN (models.py)                   │
│  Vote, Tension, Aim, Participant, VotingSession         │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  VIEW COMPONENTS                        │
│  ScaleView, AimView, VoteMarker, TensionCard           │
│  (can be customized/themed)                            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  INPUT ADAPTERS                         │
│  ClickInput, DragInput, KeyboardInput, HardwareInput   │
│  (device-specific, same interface)                     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  LAYOUT CONTROLLERS                     │
│  DesktopLayout, MobileLayout, KioskLayout              │
│  (responsive composition)                              │
└─────────────────────────────────────────────────────────┘
```

### Domain Objects

**VotingSession** (new)
```
- session_id: str
- project: Project
- round: VotingRound (BASELINE | COMPARISON)
- participant: Participant
- tensions: List[Tension]  # ordered sequence
- current_index: int       # which tension is active
- votes: Dict[tension_id, int]  # pending votes
- status: SessionStatus (IN_PROGRESS | SUBMITTED)
```

**Vote** (existing, enhanced)
```
- participant, tension_id, round, value
- context: VoteContext (device, input_method, timestamp)
```

### View Components (customizable)

**ScaleView** — The 11-position scale
- Renders positions -5 to +5
- Highlights current selection
- Can be horizontal or vertical
- *Customization*: tick style, colors, animation

**AimView** — Displays one Aim
- Shows label and optional description
- Position: left/right (horizontal) or top/bottom (vertical)
- *Customization*: typography, icons, colors

**VoteMarker** — The indicator of selected position
- Shows where the vote is placed
- *Customization*: icon, shape, color, animation (this is what Bob mentioned — someone might want their own icon)

**TensionCard** — Container for one tension
- Composes: AimView (left) + ScaleView + AimView (right) + VoteMarker
- Handles layout switching (horizontal ↔ vertical)

**VotingProgress** — Shows progress through tensions
- "3 of 7 tensions"
- Navigation controls (back/next/submit)

### Input Adapters (device-agnostic)

All implement a common interface:
```python
class VoteInput(Protocol):
    def on_value_change(self, callback: Callable[[int], None]) -> None
    def get_current_value(self) -> Optional[int]
    def set_value(self, value: int) -> None
    def enable(self) -> None
    def disable(self) -> None
```

**ClickInput** — Click/tap on position
**DragInput** — Drag slider along scale
**KeyboardInput** — Arrow keys, number keys
**HardwareInput** — Future: physical dial/buttons

### Layout Controllers

**DesktopLayout**
- Horizontal scale
- Aims on left/right sides
- Keyboard shortcuts enabled

**MobileLayout**
- Detects orientation
- Portrait: vertical scale or compact horizontal
- Landscape: horizontal scale
- Touch-optimized hit targets

**KioskLayout** (future)
- Full-screen, minimal UI
- Optimized for hardware input

---

## Implementation Phases

### Phase 1: Core Voting (MVP)
- [ ] VotingSession model
- [ ] TensionCard component (horizontal)
- [ ] ClickInput adapter
- [ ] Desktop layout
- [ ] Basic navigation (next/back/submit)

### Phase 2: Mobile Support
- [ ] MobileLayout with responsive breakpoints
- [ ] DragInput adapter
- [ ] Touch-optimized hit targets
- [ ] Vertical scale option

### Phase 3: Customization
- [ ] Themeable components (colors, fonts)
- [ ] Custom VoteMarker support
- [ ] Branded AimView options

### Phase 4: Advanced Input
- [ ] KeyboardInput adapter
- [ ] Accessibility (screen reader, focus management)
- [ ] HardwareInput adapter (for future devices)

---

## Design Decisions (Resolved)

1. **Scale display**: 11 dots only — no numeric labels shown to user. Clean, visual.
2. **User identity**: Assume known user for MVP. User self-labels (enters display name). Security/auth TBD.
3. **Submission**: User explicitly submits. Two modes supported:
   - **One-by-one**: Submit each vote as they go
   - **Batch**: Vote on all tensions, then submit all at once

## Questions to Resolve

1. **Vote editing**: Can participants change votes before submission? (Spec says yes, while voting is open)
2. **Real-time display**: Do votes appear on the facilitator view immediately, or only after submission?
3. **Comparison context**: When voting comparison round, should participants see their baseline votes?

---

## Next Steps

1. Review and refine this charter
2. Define the component interfaces in Python/TypeScript
3. Build Phase 1 (TensionCard + ClickInput) as a prototype
4. Test on desktop and mobile

---

## Database Setup (Neon + Vercel)

### 1. Install dependencies
```bash
cd /Users/kevin/Projects/intension-viewer
npm install
```

### 2. Get DATABASE_URL from Vercel
Go to Vercel dashboard → intension-viewer-rdr → Settings → Environment Variables
Copy the `DATABASE_URL` value.

### 3. Set up schema
```bash
export DATABASE_URL="postgres://..."
npm run db:setup
```

### 4. Seed demo data
```bash
npm run db:setup      # Creates tables
node scripts/seed-demo.js  # Creates demo project
```

### 5. Deploy
Push to GitHub, Vercel auto-deploys.

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/project` | GET | Get project by id or code |
| `/api/project` | POST | Create new project |
| `/api/session` | POST | Start voting session |
| `/api/session` | GET | Get session + votes |
| `/api/session` | PUT | Update session status |
| `/api/vote` | POST | Submit/update a vote |
| `/api/vote` | GET | Get votes |
