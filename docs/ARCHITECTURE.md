# In/Tension Architecture Guide

Welcome, Suliman! This document explains the architectural principles behind the In/Tension tool.

---

## Core Principle: Domain-Driven Design

We start with the **domain model**, not the screens. The domain is the "what" — the real-world concepts the software represents. The UI is just one way to interact with those concepts.

### The Domain (from the spec)

```
Project
  └── Tension (a pair of aims to balance)
        ├── Aim (left) — one strategic goal
        ├── Aim (right) — the opposing goal
        └── Votes — how participants balance them
              ├── Baseline round (how we ARE)
              └── Comparison round (how we SHOULD BE)
```

**Key insight:** A Tension is the core concept. Everything else supports it — projects contain tensions, participants vote on tensions, results visualize tensions.

---

## Layered Architecture

We separate concerns into layers. Each layer has one job.

```
┌─────────────────────────────────────────────┐
│              UI (HTML/JS)                   │  ← What users see
├─────────────────────────────────────────────┤
│              API Routes                     │  ← HTTP interface
├─────────────────────────────────────────────┤
│              Domain Model                   │  ← Business logic
├─────────────────────────────────────────────┤
│              Database                       │  ← Persistence
└─────────────────────────────────────────────┘
```

### Why layers?

- **Change one thing without breaking others.** New UI? Same API. New database? Same domain model.
- **Test in isolation.** Domain logic can be tested without a browser.
- **Understand quickly.** Each file has one purpose.

---

## File Structure

```
intension-viewer/
├── api/                    # API layer (Vercel serverless functions)
│   ├── db.js              # Database connection helper
│   ├── project.js         # Project CRUD
│   ├── session.js         # Voting session management
│   ├── vote.js            # Vote submission
│   └── results.js         # Results aggregation
│
├── public/                 # UI layer (static HTML + JS)
│   ├── vote.html          # Participant voting interface
│   └── results.html       # Results visualization
│
├── models.py              # Domain model (Python, for reference/generation)
├── views.py               # SVG rendering (Python)
│
├── scripts/               # Utilities
│   ├── setup-db.js        # Create database schema
│   └── seed-demo.js       # Load demo data
│
└── docs/                  # Documentation
    ├── ARCHITECTURE.md    # This file
    └── viewer-model.md    # Results viewer object model
```

---

## Key Principles

### 1. Spec is Source of Truth

The original specification (`intension-spec.pdf`) defines:
- Terminology (use these exact words)
- User roles and permissions
- Screen inventory and behaviors
- Data relationships

When in doubt, check the spec.

### 2. Object-Oriented Modeling

Each concept becomes a class/object with:
- **State** (data it holds)
- **Behavior** (actions it can perform)
- **Relationships** (how it connects to others)

Example — `Vote`:
```
Vote
├── Context: Who voted on what, in which round
├── Focus: The actual value (0-10)
└── Lifecycle: When submitted, when edited
```

### 3. Separation of Concerns

| Layer | Responsibility | Doesn't Know About |
|-------|----------------|-------------------|
| UI | Display and interaction | Database |
| API | HTTP, validation, coordination | How UI renders |
| Domain | Business rules and logic | HTTP or SQL |
| Database | Persistence | Business rules |

### 4. Data Flows Down, Events Flow Up

```
User clicks → UI captures → API validates → Domain processes → Database stores
                                                    ↓
User sees ← UI renders ← API responds ← Domain returns ← Database returns
```

### 5. Progressive Enhancement

Build simple, then add complexity:
1. First: Static HTML that shows data
2. Then: JavaScript for interactivity
3. Then: Real-time updates (WebSockets)
4. Then: Offline support (if needed)

We're at step 2.

---

## Database Schema

Six tables, matching the domain:

| Table | Purpose |
|-------|---------|
| `projects` | Workshop containers |
| `tensions` | The continuums (pairs of aims) |
| `participants` | People who vote |
| `votes` | Individual vote records |
| `consent_points` | Facilitator overrides |
| `voting_sessions` | Tracks voting progress |

Relationships:
```
projects 1──N tensions 1──N votes N──1 participants
                       1──N consent_points
```

---

## API Design

RESTful endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/project` | GET | Get project by ID or code |
| `/api/project` | POST | Create new project |
| `/api/session` | POST | Start voting session |
| `/api/session` | GET | Get session + votes |
| `/api/vote` | POST | Submit/update vote |
| `/api/results` | GET | Get aggregated results |

All return JSON. Errors include `{ error: "message" }`.

---

## Visualization Model

Results display uses this structure:

```
ContinuumResult
├── tension (name, aims)
├── distribution[11] — count at each position (0-10)
├── voteDetails[] — who voted where
├── consentPoint — average or override
└── yourVote — highlighted if viewing own
```

Visual components:
- **VoteBlock** — rectangle in a stack (customizable)
- **AverageMarker** — circle on the line
- **Fulcrum** — triangle at center
- **AimLabels** — text on left/right

---

## Questions to Ask Yourself

When building a feature:

1. **What domain concepts are involved?** (Check the spec's terminology)
2. **What data needs to persist?** (Database schema)
3. **What operations are needed?** (API endpoints)
4. **How will users interact?** (UI screens)
5. **What can change independently?** (Keep it in separate layers)

---

## Next Steps for New Contributors

1. Read `intension-spec.pdf` — understand the domain
2. Try the demo — vote at `/vote.html?code=DEMO01`, view at `/results.html?code=DEMO01`
3. Trace a vote — follow the code from UI → API → Database → Results
4. Pick a screen from the inventory that isn't built yet
5. Ask: What domain objects? What API? What UI?

Welcome aboard!
