# Writer Copilot AI

An **offline-first AI writing assistant** designed to help you generate, structure, and expand stories while maintaining complete control over your data and workflow. Built for creators who want intelligent plots, not just random text generation.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Flask](https://img.shields.io/badge/Flask-3.1.3-green) ![License](https://img.shields.io/badge/License-MIT-orange)

---

## 🎯 Why Writer Copilot AI?

Most AI writing tools generate text in isolation. Writer Copilot is built around a **structured creative workflow**:

```
Think (Input Parameters) → Generate (Multiple Plots) → Choose (Select Direction) → Expand (Build Full Stories)
```

All processing happens **locally** on your machine—complete privacy, no cloud dependencies.

---

## ✨ Core Features

### 📋 **Session-Based Writing System**
- Create multiple independent writing sessions
- Each session stores story parameters, generated plots, and drafts
- Switch seamlessly between different ideas and projects
- Persistent session history with timestamps

### 🎬 **Intelligent Plot Generation**
Generate multiple structured plotlines from your creative inputs:
- **Core Idea**: 3–5 sentence premise
- **Protagonist**: Character introduction
- **Conflict**: Central struggle
- **Stakes**: What's at risk
- **Direction**: Where the story heads

Each plot is unique and imaginative—designed to help you explore narrative possibilities before committing.

### 📖 **Plot-to-Story Workflow**
- Select a generated plot you like
- Generate a story opening based on that specific plot
- AI maintains narrative consistency from your plot parameters
- Reduce randomness and improve story coherence

### ✍️ **Story Continuation with AI**
- Continue writing seamlessly with AI assistance
- Preserve tone, pacing, and character consistency
- AI remembers your story context
- Generate exact word counts as needed

### 💾 **Draft Management**
- Auto-save story drafts with timestamps
- Track plot-to-story associations
- Reject and delete unwanted plots/drafts
- Reuse and modify previous drafts

### 🎨 **Customizable Formatting**
- Adjust font families (Arial, Courier, Georgia)
- Dynamic font size control (10-20px)
- Real-time text preview
- Copy-to-clipboard functionality

### ⏸️ **Streaming Generation with Stop Control**
- Real-time AI output streaming
- Stop generation at any point
- Server-side request cancellation
- Clean abort handling on frontend and backend

---

## 🏗️ Architecture

### Backend Stack
- **Framework**: Flask (Python)
- **LLM Integration**: OpenAI API compatible (currently LM Studio)
- **Storage**: JSON-based session files
- **Streaming**: Server-Sent Events (SSE) with request tracking

### Frontend Stack
- **HTML/CSS/JS**: Vanilla JavaScript (no frameworks YET)
- **UI Framework**: Bootstrap 5.3
- **Icons**: Bootstrap Icons 1.11
- **Fonts**: Inter, Plus Jakarta Sans
- **Theme**: Light/Dark mode support with CSS variables

### Key Workflows
1. **Plot Generation**: User inputs → LLM prompt engineering → JSON streaming → Parse & store plots
2. **Story Generation**: Selected plot → Context-aware prompt → Streaming output → Save as draft
3. **Session Persistence**: JSON file storage in `story_sessions/` directory

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- LM Studio (or any OpenAI-compatible API)
- Local LLM running on `http://localhost:1234/v1`

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/gargshi/writer-copilot-ai.git
cd writer-copilot-ai
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment**
Create a `.env` file in the project root:
```env
# LM Studio Configuration
LMSTUDIO_BASE_URL=http://localhost:1234/v1
LMSTUDIO_API_KEY=lm-studio
LMSTUDIO_MODEL=meta-llama-3.1-8b-instruct

# Storage Folders
DRAFT_FOLDER_NAME=drafts
STORY_SESSIONS_FOLDER_NAME=story_sessions

# Flask Security
APP_SECRET_KEY=your-secret-key-here-change-in-production
```

5. **Launch LM Studio**
- Start LM Studio on your machine
- Load your preferred LLM model
- Ensure it's running on `localhost:1234`

6. **Run the Application**
```bash
python app.py
```

7. **Access Application**
Open your browser and navigate to:
```
http://localhost:5000
```

---

## 📁 Project Structure

```
writer-copilot-ai/
├── app.py                      # Flask backend & LLM integration
├── requirements.txt            # Python dependencies
├── .env                         # Configuration (create locally)
├── README.md                    # This file
├── TODO.md                      # Development roadmap
│
├── templates/
│   ├── base.html               # Base template with styling
│   ├── sessions.html           # Sessions management page
│   ├── view_session.html       # Main writing workspace
│   └── index.html              # (Currently empty)
│
├── static/
│   ├── css/
│   │   └── styles.css          # Additional styling
│   └── js/
│       └── index.js            # Frontend utilities
│
├── story_sessions/             # Session storage (JSON files)
│   └── session_*.json
│
└── drafts/                      # Story draft storage
    └── story_*.txt
```

---

## 🔌 API Endpoints

### Session Management
- `POST /create_session` - Create a new writing session
- `GET /sessions` - List all sessions page
- `GET /session/<id>` - View session details
- `GET /get_sessions` - Fetch all sessions (JSON)
- `POST /update_session` - Update session data (plots, story params)
- `POST /delete_session` - Delete a session

### Plot & Story Generation
- `POST /send_data_to_llm` - Trigger LLM for plots/story generation
  - Query: `generate=plots|story|continue`
  - Streams JSON response
- `POST /stop_generation` - Stop active generation

### Data Retrieval
- `GET /get_plots?id=<session_id>` - Get session plots
- `GET /get_story_drafts?id=<session_id>` - Get story drafts for session

---

## ⚙️ Configuration

### LM Studio Setup
1. Download [LM Studio](https://lmstudio.ai/)
2. Load any Llama-based model (3.1 8B Instruct recommended)
3. Start the local API server (port 1234)
4. Verify by visiting `http://localhost:1234/v1/models`

### Changing the LLM Model
Edit `.env`:
```env
LMSTUDIO_MODEL=your-model-name
```

### Custom Storage Paths
```env
STORY_SESSIONS_FOLDER_NAME=my_sessions
DRAFT_FOLDER_NAME=my_drafts
```

---

## 🎮 Usage Workflow

### Step 1: Create a Session
- Navigate to "Story Sessions"
- Enter session title and description
- Click "Create Session"

### Step 2: Configure Story Parameters
- Enter main conflict, protagonist, opening scene
- Select story type (Novella/Short/Long/Novel)
- Choose narration style (First/Third Person)
- Set word count for generation

### Step 3: Generate Plots
- Set "Number of plots to generate"
- Click "Generate Plots"
- Monitor AI output in the "AI Output" panel
- Review generated plots in the main panel

### Step 4: Select & Refine
- Browse generated plots
- Click "Use this plot" to select
- Edit plot details if needed
- Click "Reject Plot" to remove unwanted ones

### Step 5: Generate Story
- Click "Generate Story" based on selected plot
- AI creates opening scene maintaining plot coherence
- Adjust font and size using formatting tools

### Step 6: Continue & Save
- Click "Continue with AI" to expand the story
- Click "Save" to save story draft
- View all drafts in the "Drafts" section
- Delete or reuse previous drafts

---

## 🔍 Key Technical Highlights

### Smart Prompt Engineering
- Structured prompts with strict JSON schemas
- Clear field constraints and critical rules
- Character consistency enforcement
- Word count targeting

### Streaming Architecture
- Real-time token streaming for responsive UX
- Request ID tracking for cancellation
- Thinking block filtering (optional `[THINK]` tags)
- Graceful abort handling

### Session Persistence
- JSON-based storage for transparency
- Timestamp tracking for all artifacts
- UUID generation for unique identification
- Duplicate plot detection

### Frontend Features
- Local storage for UI preferences (font, size)
- Real-time form syncing
- Accordion-based navigation
- Dark mode support via CSS variables

---

## 🐛 Known Limitations & Issues

1. **Element ID Collisions** - `protagonist` field appears twice; can cause form sync issues
2. **Global Variable Leaks** - Some variables not declared with `const`/`let`
3. **No Request Timeouts** - Long-stalled API calls never timeout
4. **Unbounded localStorage** - No cleanup mechanism for cached data
5. **Textarea HTML Rendering** - HTML tags output as literal text, not formatted

---

## � Roadmap

Writer Copilot is on a journey to become a complete AI-powered writing engine!

### Current Phase: **Stabilization** (Q2 2026)
Focus on reliability, bug fixes, and code quality.

### Upcoming Phases:
1. **Core Writing Features** - Character sheets, world building, scene outlines
2. **Advanced AI** - Style transfer, dialogue generation, multi-provider LLM support
3. **Export & Publishing** - PDF, EPUB, Word, Markdown formats
4. **Analytics** - Writing metrics, productivity tracking, quality scoring
5. **Collaboration** - Multi-user editing, comments, real-time sync (v2.0+)

📖 **[See Full Roadmap →](ROADMAP.md)**

---

## 🛠️ Development

### Setting Up Dev Environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Running with Debug Mode
Flask debug mode is enabled by default. Code changes auto-reload.

### Database/Storage
Sessions are stored as JSON files. No database setup required.

---

## 📝 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.1.3 | Web framework |
| OpenAI | 2.28.0 | LLM client |
| python-dotenv | 1.2.2 | Environment config |
| Werkzeug | 3.1.6 | WSGI utilities |
| Jinja2 | 3.1.6 | Template engine |

See `requirements.txt` for complete list.

---

## 🤝 Contributing

Contributions are welcome! Areas of interest:
- Bug fixes (especially form ID collisions)
- Performance optimization
- Frontend framework migration (React/Vue)
- Additional LLM provider support
- Export functionalities

---

## 📄 License

MIT License - feel free to use, modify, and distribute.

---

## 🙋 Support & Feedback

- Report issues via GitHub Issues
- Check `TODO.md` for planned features
- Questions? Open a Discussion thread

---

## 🎯 Future Vision

Writer Copilot is evolving from a simple plot generator into a **complete creative assistant** that understands:
- Story structure and pacing
- Character development arcs
- Theme consistency
- Dialogue realism
- World-building coherence

All while respecting your creative agency and keeping everything local.

---

## ⭐ Show Your Support

If Writer Copilot helps your creative process, please star this repository!

**Happy writing! 🚀**