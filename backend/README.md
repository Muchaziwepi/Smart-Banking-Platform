# Member 1 Backend Starter

This is an educational API for the AI-Assisted Smart Banking Platform. It is not production banking software.

## 1. Install
Run these commands from this folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For a quick SQLite test, leave `DATABASE_URL` unset. The app creates `smart_banking.db` automatically.
For PostgreSQL, set `DATABASE_URL` to your PostgreSQL connection string before starting the server.

## 2. Start
```powershell
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs

## 3. Test the API
1. `POST /auth/register`
2. `POST /auth/login`, copy `access_token`
3. Click **Authorize** in Swagger and enter the token (Swagger may accept `Bearer <token>` depending on its prompt).
4. `POST /accounts`
5. Use the returned account `id` for deposit, withdrawal, transaction history, and forecast.
6. Create a second account/user if you want to test transfers. The destination account number must be known.

## Important
- Use demo data only; never use real bank credentials or real customer information.
- This starter has basic authentication and demo business logic. It is not audited or hardened for production.
- Before deploying beyond a class demo, add database migrations, rate limiting, stronger secret management, audit logging, concurrency-safe ledger operations, and security review.
