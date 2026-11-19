# Smart Banking Platform

This project contains the React/Vite frontend and FastAPI backend in one folder. It is an academic simulation only, not production banking software. Use demo data only.

## Folder structure

- `frontend/` — React + Vite user interface
- `backend/` — FastAPI API, authentication and database models

## Requirements

- Node.js LTS and npm
- Python 3.10+ (recommended)

## Start the backend (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend API: http://127.0.0.1:8000  
API documentation: http://127.0.0.1:8000/docs

The backend uses SQLite by default and creates its database automatically. For PostgreSQL, copy `.env.example` to `.env` and set `DATABASE_URL` and a strong `JWT_SECRET_KEY`.

## Start the frontend

Open a second terminal while the backend is running:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

CORS is configured in the backend for the local Vite addresses above. Start the backend before using login and banking features.

## Notes

- `.venv`, Python cache files and the local SQLite database were not packaged; Python dependencies are installed from `backend/requirements.txt`.
- The frontend stores its demo token and local savings goals in browser local storage.
- Do not use real bank credentials, customer data, or real funds.
