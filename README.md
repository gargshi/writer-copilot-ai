# ✍️ Writer Copilot (Offline AI Writing Assistant)

An offline-first AI-powered writing assistant designed to help you **generate, continue, and refine stories** — all running locally with your own LLM.

---

## 🚀 Overview

Writer Copilot is a lightweight web application that integrates with a **locally hosted LLM (via LM Studio)** to assist writers in crafting compelling stories.

Unlike cloud-based tools, this project focuses on:

* 🔒 Privacy (no external API calls required)
* ⚡ Speed (local inference)
* 💡 Creativity support (not just generation)

---

## ✨ Features

### 🧠 AI Story Generation

* Generate story openings based on:

  * Protagonist
  * Conflict
  * Setting
  * Story type
  * Narrative perspective

### 🔄 Continue Writing with AI

* Extend your story seamlessly
* Maintains tone and narrative flow
* Controlled generation (~300 words for continuation)

### 💾 Draft Management

* Save stories locally as drafts
* View all saved drafts
* Load and continue editing
* Delete drafts when needed

### ⚡ Streaming Responses

* Real-time text generation from the LLM
* Optional handling of model "thinking" blocks (`[THINK]`)

### 🛑 Stop Generation

* Interrupt AI generation mid-way
* Useful for controlling output length

---

## 🏗️ Tech Stack

* **Backend:** Flask (Python)
* **LLM Integration:** Local model via LM Studio (OpenAI-compatible API)
* **Frontend:** HTML, CSS, JavaScript
* **Storage:** Local file system (`.txt` drafts)
* **Environment Config:** `.env`

---

## 📂 Project Structure

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
├── drafts/              # Stored stories
├── app.py               # Main Flask app
├── .env                 # Environment variables
├── .gitignore
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd writer-copilot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # (Linux/Mac)
.venv\Scripts\activate     # (Windows)
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup `.env`

Create a `.env` file:

```
LMSTUDIO_BASE_URL=http://localhost:1234/v1
LMSTUDIO_API_KEY=lm-studio
LMSTUDIO_MODEL=your-model-name
DRAFT_FOLDER_NAME=drafts
```

---

## 🧪 Running the App

```bash
python app.py
```

Then open:

```
http://127.0.0.1:5000
```

---

## 🧠 How It Works

1. User provides story parameters
2. Flask backend builds a structured prompt
3. Request is sent to local LLM (via LM Studio)
4. Response is streamed back in real time
5. Drafts are saved locally for persistence

---

## 🔐 Privacy & Offline Design

* No external API calls required
* All data stays on your machine
* Drafts are stored locally
* Ideal for privacy-conscious writers

---

## ⚠️ Current Limitations

* No authentication (single-user, offline design)
* File-based storage (no database yet)
* Basic UI (focused on functionality first)
* Depends on locally running LLM

---

## 🛣️ Future Improvements

* 📊 Story structuring assistance (plot, arcs, pacing)
* 🧠 Writing feedback & suggestions (not just generation)
* 🗂️ Draft tagging & organization
* 🧾 Version history
* 🧩 Plugin-style writing tools (dialogue enhancer, tone shifter)
* 🌐 Optional cloud sync

---

## 💡 Vision

This project is not just about generating text —
it aims to become a **true writing companion** that helps users improve their storytelling skills over time.

---

## 🤝 Contributing

Feel free to fork and experiment. Suggestions and improvements are welcome!

---

## 📜 License

MIT License (or choose your preferred license)

---

## 👨‍💻 Author

Built as part of an exploration into:

* Local LLM applications
* Creative AI tooling
* Human-AI collaboration in writing

---

✨ *Write better. Think deeper. Stay in control.*
