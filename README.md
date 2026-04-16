# Writer Copilot AI

An offline-first AI writing assistant designed to help you generate, structure, and expand stories while maintaining control over your data and workflow. Writer Copilot AI is built around a guided writing process: define the brief, generate plot options, pick a direction, shape the cast, and draft with AI support.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.1.3-green)
![License](https://img.shields.io/badge/License-MIT-orange)

---

## Why Writer Copilot AI?

Most AI writing tools generate text in isolation. Writer Copilot is built around a structured creative workflow:

```text
Think (Input Parameters) -> Generate (Plot Options) -> Choose (Select Direction) -> Expand (Draft the Story)
```

All processing happens locally on your machine through an OpenAI-compatible endpoint such as LM Studio.

---

## Core Features

### Session-Based Writing System
- Create multiple independent writing sessions
- Store story parameters, plots, characters, and drafts per session
- Switch between projects without losing context
- Keep persistent session history with timestamps

### Intelligent Plot Generation
- Generate one or more structured plot options from a story brief
- Each plot includes core idea, protagonist, conflict, stakes, direction, and timeline
- Compare options before committing to a direction

### Plot-to-Story Workflow
- Select a generated plot and promote it into the active workspace
- Generate a story opening based on the selected plot
- Continue the story while preserving context and direction

### Character Management
- Add characters manually
- Generate characters from the selected plot
- Edit and delete characters inside a session

### Draft Management
- Save story drafts with timestamps
- Reopen earlier drafts
- Delete drafts you no longer want to keep

### Streaming Generation with Stop Control
- Stream model output in real time
- Stop an active generation request
- Cancel requests on the backend using request IDs

### Editor Customization
- Change font family
- Adjust font size
- Copy story text
- Download the current draft as a text file

---

## Architecture

### Backend Stack
- Flask
- OpenAI Python client
- LM Studio-compatible local API
- JSON file storage for sessions, plots, drafts, and characters

### Frontend Stack
- Vanilla JavaScript
- Bootstrap
- Bootstrap Icons
- CSS variables for theme support

### Key Workflows
1. Plot generation: form inputs -> prompt construction -> streamed JSON -> parse and store plots
2. Story generation: selected plot -> context-aware prompt -> streamed story -> save as draft
3. Session persistence: JSON file storage in local project folders

---

## Getting Started

### Prerequisites
- Python 3.8 or higher
- LM Studio or another OpenAI-compatible local API
- A model loaded and available through the local API server

### Installation

1. Clone the repository

```bash
git clone https://github.com/gargshi/writer-copilot-ai.git
cd writer-copilot-ai
```

2. Create a virtual environment

```bash
python -m venv venv
```

3. Activate the virtual environment

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

4. Install dependencies

```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the project root

```env
# LM Studio Configuration
LMSTUDIO_BASE_URL=http://localhost:1234/v1
LMSTUDIO_API_KEY=lm-studio
LMSTUDIO_MODEL=qwen/qwen3-4b

# Storage Folders
DRAFT_FOLDER_NAME=drafts
STORY_SESSIONS_FOLDER_NAME=story_sessions
CHARACTERS_FOLDER_NAME=characters
PLOT_FOLDER_NAME=plots

# Flask Security
APP_SECRET_KEY=your-secret-key-here-change-in-production
```

6. Start LM Studio and make sure the local API server is running

7. Run the application

```bash
python app.py
```

8. Open the app

```text
http://localhost:5000
```

---

## Project Structure

```text
writer-copilot-ai/
|-- app.py
|-- requirements.txt
|-- README.md
|-- TODO.md
|-- templates/
|   |-- base.html
|   |-- sessions.html
|   |-- view_session_updated.html
|   `-- index.html
|-- static/
|   |-- css/
|   |   `-- styles.css
|   `-- js/
|       `-- index.js
|-- story_sessions/
|   `-- session_*.json
|-- plots/
|   `-- plot_*.json
|-- drafts/
|   `-- draft_*.json
`-- characters/
    `-- character_*.json
```

---

## API Endpoints

### Session Management
- `POST /create_session` - Create a new writing session
- `GET /` - Sessions page
- `GET /session/<id>` - View a session workspace
- `GET /get_sessions` - Fetch all sessions as JSON
- `POST /update_session` - Update session data
- `POST /delete_session` - Delete a session

### Plot and Story Generation
- `POST /send_data_to_llm` - Generate `plots`, `story`, `continue`, or `character`
- `POST /stop_generation` - Stop an active generation request
- `GET /lmstudio/load_model` - Get LM Studio model load status
- `POST /lmstudio/load_model` - Load the configured LM Studio model

### Data Retrieval
- `GET /get_plots?id=<session_id>` - Get plots for a session
- `GET /drafts?id=<session_id>` - Get drafts for a session
- `GET /characters?id=<session_id>` - Get characters for a session

---

## Configuration

### LM Studio Setup
1. Download [LM Studio](https://lmstudio.ai/)
2. Load a supported model
3. Start the local API server
4. Point `LMSTUDIO_BASE_URL` to the running server

### Custom Storage Paths

```env
STORY_SESSIONS_FOLDER_NAME=my_sessions
DRAFT_FOLDER_NAME=my_drafts
CHARACTERS_FOLDER_NAME=my_characters
PLOT_FOLDER_NAME=my_plots
```

---

## Usage Workflow

### Step 1: Create a Session
- Create a session with a title and description

### Step 2: Configure Story Parameters
- Enter main conflict, protagonist, and opening scene
- Select story type and narration style
- Set the number of plots and target word count

### Step 3: Generate Plots
- Generate plot options from the story brief
- Review them in the plot library

### Step 4: Select a Direction
- Use a plot to load it into the selected plot workspace
- Reject plots you do not want to keep

### Step 5: Shape the Cast
- Add characters manually or generate them from the selected plot

### Step 6: Draft and Continue
- Generate the opening story draft
- Continue the story with AI
- Save useful drafts as checkpoints

---

## Key Technical Highlights

### Prompt Engineering
- Structured prompts with strict JSON output expectations
- Separate generation modes for plots, stories, continuation, and characters
- Character and continuity constraints built into prompts

### Streaming Architecture
- Real-time response streaming
- Request tracking for cancellation
- Backend stop control for active generations

### Local Persistence
- JSON-based storage for transparency and portability
- UUID-based file identities
- Per-session linkage between plots, drafts, and characters

---

## Known Limitations

- Storage is file-based rather than database-backed
- Prompt and response validation can still be improved
- The app is tuned for local usage and development workflows
- Automated tests are not yet in place

---

## Roadmap

Planned future improvements include:

- better validation and cleanup flows
- richer editor and drafting tools
- export options beyond plain text
- additional model/provider flexibility
- stronger production readiness

See [ROADMAP.md](ROADMAP.md) for longer-term direction.

---

## Development

### Local Development

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Storage

No database setup is required. Sessions, plots, drafts, and characters are stored as JSON files in local folders.

---

## Dependencies

Core packages used in this project:

- Flask
- OpenAI
- python-dotenv
- httpx
- Werkzeug
- Jinja2

See `requirements.txt` for the full dependency list.

---

## Contributing

Contributions are welcome. Useful areas include:

- bug fixes
- UI polish
- prompt and output validation improvements
- export features
- testing and reliability improvements

---

## License

MIT License.

---

## Support

- Open an issue for bugs or feature requests
- Check `TODO.md` for planned work
- Review `ROADMAP.md` for upcoming goals

---

## Show Your Support

If this project helps your writing workflow, consider starring the repository.
