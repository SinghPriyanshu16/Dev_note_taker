# Dev Note-Taker & Code Summarizer

An internal tool designed to help developers quickly process meeting transcripts, raw notes, and pull request descriptions. 

It leverages AI to automatically generate:
- Markdown documentation
- Key action items
- Flags for potential technical debt

## Tech Stack
- **Backend:** Python / Flask
- **Frontend:** Vanilla HTML/CSS/JS (with Marked.js for markdown rendering)
- **AI:** Google Gemini API

## Setup Instructions

1. **Clone the repository** (or download the files).

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Copy `.env.example` to a new `.env` file and add your Gemini API key.
   ```bash
   cp .env.example .env
   # Edit .env and insert your GEMINI_API_KEY
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. Open your browser to `http://localhost:5000`

## Why this tool?
We often have lengthy technical discussions or messy PR descriptions. This tool cuts down the manual overhead of writing clean docs and ensures we don't forget follow-ups (action items) or brush over code smells (tech debt). I built this quickly to solve my own pain point, but structured it so anyone on the team can use it!
