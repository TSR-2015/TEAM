# TeamBrain AI

An AI-powered team assistant that integrates with GitHub, tracks meetings, and maintains a shared team memory.

## Project Structure

```text
teambrain-ai/
│
├── app/
│   ├── main.py             # Application entrypoint
│   ├── config.py           # Configuration & environment variables
│   ├── models.py           # Data models (Pydantic / Database)
│   ├── memory.py           # Shared team memory logic
│   ├── ai.py               # AI & LLM integration logic
│   ├── github_webhook.py   # GitHub webhook event handler
│   ├── meetings.py         # Meeting analysis & summary logic
│   ├── routes.py           # FastAPI routes
│   └── utils.py            # Utility helper functions
│
├── data/
│   ├── memories/           # Persistent memory storage
│   ├── meetings/           # Meeting transcripts & summaries
│   └── uploads/            # Temporary file uploads
│
├── tests/                  # Test suite
│
├── .env                    # Environment configuration
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation
```

## Setup Instructions

1. **Create and Activate Virtual Environment:**
   ```bash
   python -m venv .venv
   ```
   - Windows:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Copy the template values in `.env` and fill them out.

4. **Run the Application:**
   ```bash
   uvicorn app.main:app --reload
   ```
