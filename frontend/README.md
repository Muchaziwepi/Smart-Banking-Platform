# SmartBank AI – React Frontend

This frontend is designed to connect to the uploaded FastAPI backend starter.

## Requirements
- Python backend already running at `http://127.0.0.1:8000`
- Node.js LTS and npm

## Run
Open a terminal in this folder:

```powershell
npm install
npm run dev
```

Open http://localhost:5173

## Backend connection
The frontend calls `http://127.0.0.1:8000`. Start the backend separately:

```powershell
# In the backend folder, with its virtual environment activated
uvicorn app.main:app --reload
```

## Important: enable CORS in the backend
In `app/main.py`, add this import:

```python
from fastapi.middleware.cors import CORSMiddleware
```

Immediately after `app = FastAPI(...)` is defined, add:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Restart Uvicorn after changing the backend.

## Included features
- Register/login using backend JWT authentication
- Accounts, deposits, withdrawals and transaction history
- Financial health score (transparent demo heuristic)
- Spending categorisation based on transaction descriptions
- Rule-based anomaly alerts
- What-If savings simulator and backend forecast
- Local savings goals
- Educational loan application support
- Local rule-based assistant using loaded account data

This is an academic simulation, not production banking software. Fraud alerts and financial health scoring are illustrative only.
