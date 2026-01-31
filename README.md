# Chat UI (FastAPI + OpenAI)

Minimal chat app with a browser UI. The UI creates chat sessions, sends messages to OpenAI models, and shows full history with total tokens and total cost.

## How to run
### 1) Install
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2) Configure
Create `.env` in the project root:
```env
OPENAI_API_KEY=your_key_here

# optional
DATABASE_URL=sqlite:///./app.db
OPENAI_MODEL=gpt-4o-mini
CONTEXT_LIMIT=30
SYSTEM_PROMPT=You are a helpful assistant.
```

### 3) Start the server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Use in browser
Open:
- **http://127.0.0.1:8000/**

In the UI, you can select a model (gpt-4o-mini or gpt-4o), start a new chat by clicking New session, then type a message and send it with Send (or by pressing Enter). The top bar displays the current Session ID, total token usage, and the total accumulated cost for the session.

## Notes
- Conversation history is stored in the database (`app.db` by default).
- Token pricing is defined in `app/services/pricing.py` (`RATES`).
