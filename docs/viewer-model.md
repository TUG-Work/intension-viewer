# Results Viewer Object Model

## Purpose

Display votes stacked and distributed on a continuum, allowing participants and facilitators to see how the group voted on each tension.

## Object Model

```
┌─────────────────────────────────────────────────────────────────┐
│                        ResultsView                               │
│  - project: Project                                              │
│  - round: "baseline" | "comparison"                              │
│  - participantCount: number                                       │
│  - results: ContinuumResult[]                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ContinuumResult                             │
│  - tension: TensionView                                          │
│  - voteCount: number                                             │
│  - distribution: number[11]    // count at each position 0-10   │
│  - voteDetails: VoteDetail[]   // individual votes              │
│  - average: number | null                                        │
│  - consentPoint: number | null                                   │
│  - isManualConsent: boolean                                      │
│  - yourVote: number | null     // highlighted if viewing own    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        VoteDetail                                │
│  - position: number (0-10)                                       │
│  - participantId: string                                         │
│  - displayName: string                                           │
│  - isYou: boolean              // true if this is viewer's vote │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        TensionView                               │
│  - id: string                                                    │
│  - name: string                                                  │
│  - leftAim: AimView                                              │
│  - rightAim: AimView                                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         AimView                                  │
│  - label: string                                                 │
│  - description: string | null                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Visual Components

### ContinuumCard

Container for one tension's results.

**Contains:**
- Header (tension name, vote count, average)
- Legend (vote colors, your vote indicator, average marker)
- ContinuumViz (the actual visualization)

### ContinuumViz

The visual representation of vote distribution.

**Elements:**
- **Scale line**: Horizontal line representing the spectrum
- **Fulcrum**: Triangle at center (balance point)
- **Vote stacks**: Columns of vote blocks at each position (0-10)
- **Aims**: Labels on left and right ends
- **Average marker**: Circle positioned at the consent point

### VoteBlock

Individual vote rectangle in a stack.

**Properties:**
- `position`: Which column (0-10)
- `isYou`: Highlighted if viewer's vote
- `initials`: First letters of participant name
- `displayName`: Full name (tooltip)

**Customization points:**
- Color (default: light blue; yours: dark blue)
- Shape (default: rounded rectangle)
- Content (default: initials)

### AverageMarker

Circle showing the consent point.

**Position:** Calculated from average, placed on the scale line.
**Customizable:** Color, size, shape.

## API Response Format

```json
{
  "project": {
    "id": "demo-march-2025",
    "name": "AI Strategy Session - March 2025"
  },
  "round": "baseline",
  "participantCount": 6,
  "results": [
    {
      "tension": {
        "id": "t_quality_quantity",
        "name": "Quality vs Quantity of Outputs",
        "leftAim": { "label": "Quality", "description": "Focus on excellence" },
        "rightAim": { "label": "Quantity", "description": "Focus on volume" }
      },
      "voteCount": 6,
      "distribution": [1, 2, 0, 1, 1, 1, 0, 0, 0, 0, 0],
      "voteDetails": [
        { "position": 0, "participantId": "p_abc", "displayName": "Alice", "isYou": false },
        { "position": 1, "participantId": "p_def", "displayName": "Bob", "isYou": true },
        // ...
      ],
      "average": 2.33,
      "consentPoint": 2.33,
      "isManualConsent": false,
      "yourVote": 1
    }
  ]
}
```

## Usage

### View results (anonymous)
```
/results.html?code=DEMO01
```

### View results with your vote highlighted
```
/results.html?code=DEMO01&participantId=p_abc123
```

### After voting, user is linked to results with their ID
The vote.html page includes a link after submission:
```
View Results → results.html?code=DEMO01&participantId={session.participantId}
```

## Customization Points

| Component | What Can Be Customized |
|-----------|----------------------|
| VoteBlock | Color, shape, content (initials vs icon) |
| AverageMarker | Color, size, shape |
| ContinuumViz | Layout (horizontal/vertical), colors |
| Legend | Which items to show |
| AimView | Typography, icons |
