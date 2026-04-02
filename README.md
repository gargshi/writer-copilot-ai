# Writer Copilot (Offline AI Writing Assistant)

Writer Copilot is an offline-first AI writing assistant designed to help you generate, structure, and expand stories—while keeping full control over your data and workflow.

Built for creators who want more than just text generation, it introduces a session-based writing system with plot exploration and controlled story expansion.

---

## Why Writer Copilot?

Most AI writing tools generate text in isolation. Writer Copilot is built around a workflow:

* Think → Generate plots
* Choose → Select direction
* Expand → Build full stories

All of this runs locally on your machine.

---

## Core Features

### Session-Based Writing

* Create multiple writing sessions
* Each session stores its own inputs, plots, and story
* Easily switch between different ideas/projects

---

### AI Plot Generation

Generate multiple structured plotlines from your inputs:

* Core idea
* Protagonist
* Conflict
* Stakes
* Direction

Helps you explore different narrative directions before committing.

---

### Plot Selection → Story Generation

* Select a plot you like
* Generate a story opening based on that plot
* Maintains narrative consistency
* Designed to reduce randomness and improve coherence

---

### AI Story Continuation (Streaming)

* Expand stories in real time (_being upgraded_)
* Smooth token-by-token streaming
* Maintains tone and narrative flow
* Interrupt generation anytime

---

### Draft & Session Persistence

* Save sessions locally
* Store plots and generated stories
* Reload and continue writing anytime

---

### Real-Time Streaming

* Live output from LLM
* Responsive writing experience
* Supports interruption via AbortController

---

### Stop Generation

* Cancel generation instantly
* Useful for controlling output length and direction

---

## Tech Stack

* Backend: Flask (Python)
* LLM Integration: LM Studio (OpenAI-compatible API)
* Frontend: HTML, CSS, JavaScript
* Storage: Local file system (sessions + drafts)
* Config: .env

---

## Project Structure (_tentative_)

```
project/
│
├── static/
│   ├── css/
│   └── js/
│
├── templates/
│   └── index.html
│
├── sessions/            # Stored sessions (plots + stories)
├── drafts/              # Optional saved story drafts
├── app.py               # Flask backend
├── .env                 # Environment config
├── .gitignore
└── README.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd writer-copilot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\\Scripts\\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment (_tentative_)

Create a .env file:

```
LMSTUDIO_BASE_URL=http://localhost:<port>/v1
LMSTUDIO_API_KEY=your-api-key
LMSTUDIO_MODEL=your-model-name
DRAFT_FOLDER_NAME=your-drafts-folder
STORY_SESSIONS_FOLDER_NAME=your-sessions-folder
APP_SECRET_KEY=your-secret-key
```

---

## Running the App

```bash
python app.py
```

Open in browser:

```
http://127.0.0.1:5000
```

---

## How It Works

1. User creates a session and provides story parameters
2. AI generates multiple plot options
3. User selects a plot
4. AI generates a story based on the selected plot
5. Story can be extended via streaming (feature_being_rewritten)
6. Session is saved locally for reuse (feature_being_enhanced)

---

## Privacy & Offline Design

* No external API calls required
* All processing happens locally
* Data never leaves your machine

Ideal for:

* Privacy-conscious writers
* Offline environments
* Experimenting with local LLMs

---

## Current Limitations

* Single-user system (no authentication)
* File-based storage (no database yet)
* UI is functional but not fully polished
* Output quality depends on selected local model
* No cloud sync
* LMStudio is required for hosting the LLM. (**important**)

---

## Roadmap

Planned improvements:

* Plot-to-story consistency improvements
* Story structuring tools (acts, pacing, arcs)
* Session tagging and organization
* Version history per session
* Plugin-style writing tools (dialogue enhancer, tone shifter)
* Optional cloud sync
* Story continuation is being reworked.
* Session persistence is being enhanced.

---

## Vision

Writer Copilot aims to become a structured AI writing system, not just a generator—helping users think in plots, explore ideas, and build better stories step by step.

---

## Contributing

Feel free to fork, experiment, and build on top of this project.

Suggestions and improvements are always welcome.

---

## Author

Built as part of an exploration into:

* Local LLM applications
* Creative AI tooling
* Human–AI collaboration in storytelling

---

## Tagline

Write better. Think deeper. Stay in control.
