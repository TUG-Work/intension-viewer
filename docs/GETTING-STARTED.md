# Getting Started — For Suliman

Welcome! This guide will help you set up the In/Tension project on your local machine and start contributing.

---

## Prerequisites

You'll need these installed on your computer:

| Tool | What It's For | Install |
|------|---------------|---------|
| **Git** | Version control | [git-scm.com](https://git-scm.com/downloads) |
| **Node.js** | JavaScript runtime | [nodejs.org](https://nodejs.org/) (LTS version) |
| **VS Code** | Code editor | [code.visualstudio.com](https://code.visualstudio.com/) |

### Check Your Setup

Open a terminal and run:

```bash
git --version    # Should show: git version 2.x.x
node --version   # Should show: v18.x.x or higher
npm --version    # Should show: 9.x.x or higher
```

---

## Step 1: Fork the Repository

1. Go to: **https://github.com/TUG-Work/intension-viewer**
2. Click the **"Fork"** button (top right)
3. This creates a copy under your GitHub account

You now have: `https://github.com/YOUR-USERNAME/intension-viewer`

---

## Step 2: Clone Your Fork

In your terminal:

```bash
# Navigate to where you want the project
cd ~/Projects  # or wherever you keep code

# Clone YOUR fork (replace YOUR-USERNAME)
git clone https://github.com/YOUR-USERNAME/intension-viewer.git

# Enter the project folder
cd intension-viewer
```

---

## Step 3: Set Up the Upstream Remote

This lets you pull updates from the main repository:

```bash
# Add the original repo as "upstream"
git remote add upstream https://github.com/TUG-Work/intension-viewer.git

# Verify remotes
git remote -v
# Should show:
#   origin    https://github.com/YOUR-USERNAME/intension-viewer.git
#   upstream  https://github.com/TUG-Work/intension-viewer.git
```

---

## Step 4: Install Dependencies

```bash
npm install
```

This installs the packages listed in `package.json`.

---

## Step 5: Try the Live Demo

Before running locally, see what we've built:

1. **Vote:** https://intension-viewer-rdr.vercel.app/vote.html?code=DEMO01
   - Enter your name
   - Vote on all 7 tensions
   - Submit

2. **View Results:** https://intension-viewer-rdr.vercel.app/results.html?code=DEMO01
   - See votes stacked on each continuum
   - Your vote is highlighted

---

## Step 6: Understand the Code Structure

```
intension-viewer/
├── api/                    # Backend (Vercel serverless functions)
│   ├── db.js              # Database connection
│   ├── project.js         # Project API
│   ├── session.js         # Voting session API
│   ├── vote.js            # Vote API
│   └── results.js         # Results API
│
├── public/                 # Frontend (static files)
│   ├── vote.html          # Voting interface
│   ├── results.html       # Results viewer
│   └── index.html         # Generated Python output (legacy)
│
├── scripts/               # Setup utilities
│   ├── setup-db.js        # Creates database tables
│   └── seed-demo.js       # Loads demo data
│
├── docs/                  # Documentation (read these!)
│   ├── ARCHITECTURE.md    # How the system is designed
│   ├── GETTING-STARTED.md # This file
│   └── viewer-model.md    # Results visualization model
│
├── models.py              # Domain model (Python)
├── views.py               # SVG rendering (Python)
├── package.json           # Node.js dependencies
└── vercel.json            # Vercel deployment config
```

---

## Step 7: Read the Key Documents

In this order:

1. **`docs/ARCHITECTURE.md`** — How the system is designed
2. **`intension-spec.pdf`** — The original specification (in `/source/` of the intension-tool repo)
3. **`docs/viewer-model.md`** — How results visualization works

---

## Step 8: Trace a Vote Through the Code

Follow the data flow:

1. **User votes** → `public/vote.html` (JavaScript)
2. **JS calls API** → `fetch('/api/vote', { method: 'POST', ... })`
3. **API receives** → `api/vote.js` handles the request
4. **Database stores** → SQL INSERT into `votes` table
5. **Results fetch** → `api/results.js` aggregates votes
6. **UI displays** → `public/results.html` renders the visualization

---

## Making Changes

### Create a Branch

Always work on a branch, not `main`:

```bash
# Make sure you're on main and up to date
git checkout main
git pull upstream main

# Create a new branch for your work
git checkout -b feature/my-new-feature
```

### Make Your Changes

Edit files in VS Code. Save often.

### Commit Your Changes

```bash
# See what changed
git status

# Stage changes
git add .

# Commit with a message
git commit -m "Add feature X"
```

### Push to Your Fork

```bash
git push origin feature/my-new-feature
```

### Open a Pull Request

1. Go to your fork on GitHub
2. Click **"Compare & pull request"**
3. Write a description of what you changed and why
4. Click **"Create pull request"**

Bob will review and merge (or give feedback).

---

## Staying Updated

When the main repo changes:

```bash
git checkout main
git pull upstream main
git push origin main  # Update your fork's main
```

Then update your feature branch:

```bash
git checkout feature/my-branch
git merge main
```

---

## Common Git Commands

| Command | What It Does |
|---------|--------------|
| `git status` | See what's changed |
| `git add .` | Stage all changes |
| `git commit -m "msg"` | Save changes locally |
| `git push` | Upload to GitHub |
| `git pull` | Download updates |
| `git checkout -b name` | Create new branch |
| `git checkout main` | Switch to main branch |
| `git log --oneline` | See commit history |

---

## Getting Help

- **Git concepts:** [Git Handbook](https://guides.github.com/introduction/git-handbook/)
- **VS Code + Git:** [VS Code Git Tutorial](https://code.visualstudio.com/docs/sourcecontrol/intro-to-git)
- **Questions:** Ask Bob or post in the project discussions

---

## Your First Contribution

Suggested starter tasks:

1. **Fix a typo** in documentation (easy PR to practice the flow)
2. **Add a missing aim description** in `seed-demo.js`
3. **Improve mobile styling** in `vote.html` or `results.html`
4. **Review the spec** and note any gaps between spec and implementation

---

Good luck! Remember: everyone was new once. Ask questions, make small commits, and learn by doing.
