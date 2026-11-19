from decimal import Decimal
from secrets import token_hex
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from .database import Base, engine, get_db
from . import models, schemas
from .security import hash_password, verify_password, create_access_token, decode_access_token

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="AI-Assisted Smart Banking Platform API",
    description="Academic simulation only. Do not use for real banking or real financial decisions.",
    version="1.0.0",
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    user = db.get(models.User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user

def owned_account(db: Session, account_id: int, user_id: int) -> models.Account:
    account = db.scalar(select(models.Account).where(
        models.Account.id == account_id, models.Account.owner_id == user_id
    ))
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@app.get("/")
def root():
    return {"message": "Smart Banking API is running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/register", response_model=schemas.UserOut, status_code=201)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    email = str(payload.email).lower()
    if db.scalar(select(models.User).where(models.User.email == email)):
        raise HTTPException(status_code=409, detail="Email is already registered")
    user = models.User(full_name=payload.full_name.strip(), email=email,
                       password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    email = str(payload.email).lower()
    user = db.scalar(select(models.User).where(models.User.email == email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return schemas.TokenOut(access_token=create_access_token(user.id))

@app.get("/users/me", response_model=schemas.UserOut)
def read_me(user: models.User = Depends(get_current_user)):
    return user

@app.post("/accounts", response_model=schemas.AccountOut, status_code=201)
def create_account(payload: schemas.AccountCreate, db: Session = Depends(get_db),
                   user: models.User = Depends(get_current_user)):
    account = models.Account(
        account_number="SB" + token_hex(8).upper(),
        account_type=payload.account_type,
        currency=payload.currency.upper(),
        balance=Decimal("0.00"),
        owner_id=user.id,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

@app.get("/accounts", response_model=list[schemas.AccountOut])
def list_accounts(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return list(db.scalars(select(models.Account).where(models.Account.owner_id == user.id).order_by(models.Account.id)))

@app.get("/accounts/{account_id}", response_model=schemas.AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return owned_account(db, account_id, user.id)

def add_transaction(db: Session, account: models.Account, kind: str, amount: Decimal, description: str, reference: str):
    transaction = models.Transaction(
        account_id=account.id, transaction_type=kind, amount=amount,
        description=description, reference=reference
    )
    db.add(transaction)
    return transaction

@app.post("/accounts/{account_id}/deposit", response_model=schemas.TransactionOut, status_code=201)
def deposit(account_id: int, payload: schemas.MoneyRequest, db: Session = Depends(get_db),
            user: models.User = Depends(get_current_user)):
    account = owned_account(db, account_id, user.id)
    account.balance = Decimal(account.balance) + payload.amount
    tx = add_transaction(db, account, "deposit", payload.amount, payload.description or "Deposit", token_hex(10).upper())
    db.commit()
    db.refresh(tx)
    return tx

@app.post("/accounts/{account_id}/withdraw", response_model=schemas.TransactionOut, status_code=201)
def withdraw(account_id: int, payload: schemas.MoneyRequest, db: Session = Depends(get_db),
             user: models.User = Depends(get_current_user)):
    account = owned_account(db, account_id, user.id)
    if Decimal(account.balance) < payload.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    account.balance = Decimal(account.balance) - payload.amount
    tx = add_transaction(db, account, "withdrawal", payload.amount, payload.description or "Withdrawal", token_hex(10).upper())
    db.commit()
    db.refresh(tx)
    return tx

@app.post("/accounts/{account_id}/transfer", status_code=201)
def transfer(account_id: int, payload: schemas.TransferRequest, db: Session = Depends(get_db),
            user: models.User = Depends(get_current_user)):
    source = owned_account(db, account_id, user.id)
    destination = db.scalar(select(models.Account).where(models.Account.account_number == payload.destination_account_number))
    if not destination:
        raise HTTPException(status_code=404, detail="Destination account not found")
    if destination.id == source.id:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same account")
    if destination.currency != source.currency:
        raise HTTPException(status_code=400, detail="Accounts must use the same currency for this demo transfer")
    if Decimal(source.balance) < payload.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    reference = token_hex(10).upper()
    source.balance = Decimal(source.balance) - payload.amount
    destination.balance = Decimal(destination.balance) + payload.amount
    add_transaction(db, source, "transfer_out", payload.amount, payload.description or "Transfer sent", reference)
    add_transaction(db, destination, "transfer_in", payload.amount, payload.description or "Transfer received", reference)
    db.commit()
    return {"message": "Transfer completed", "reference": reference, "amount": str(payload.amount)}

@app.get("/accounts/{account_id}/transactions", response_model=list[schemas.TransactionOut])
def transaction_history(account_id: int, limit: int = 50, db: Session = Depends(get_db),
                        user: models.User = Depends(get_current_user)):
    owned_account(db, account_id, user.id)
    limit = max(1, min(limit, 100))
    return list(db.scalars(select(models.Transaction)
        .where(models.Transaction.account_id == account_id)
        .order_by(models.Transaction.created_at.desc())
        .limit(limit)))

@app.post("/loans", response_model=schemas.LoanOut, status_code=201)
def create_loan(payload: schemas.LoanCreate, db: Session = Depends(get_db),
                user: models.User = Depends(get_current_user)):
    # Educational triage only: not underwriting and not a real approval.
    monthly_income = payload.annual_income / Decimal("12")
    debt_ratio = (payload.existing_monthly_debt / monthly_income) if monthly_income > 0 else Decimal("1")
    status_text = "needs_review" if debt_ratio > Decimal("0.40") else "submitted"
    note = (
        "Educational indicator only. A human review and real lender rules are required. "
        f"Existing monthly debt is approximately {(debt_ratio * 100):.1f}% of monthly income."
    )
    loan = models.LoanApplication(
        owner_id=user.id, requested_amount=payload.requested_amount,
        annual_income=payload.annual_income, existing_monthly_debt=payload.existing_monthly_debt,
        purpose=payload.purpose, status=status_text, note=note
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan

@app.get("/loans", response_model=list[schemas.LoanOut])
def list_loans(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return list(db.scalars(select(models.LoanApplication)
        .where(models.LoanApplication.owner_id == user.id)
        .order_by(models.LoanApplication.created_at.desc())))

@app.post("/accounts/{account_id}/forecast", response_model=schemas.ForecastOut)
def forecast(account_id: int, payload: schemas.ForecastRequest, db: Session = Depends(get_db),
             user: models.User = Depends(get_current_user)):
    account = owned_account(db, account_id, user.id)
    net = payload.monthly_income - payload.monthly_expenses
    projected = Decimal(account.balance) + net * payload.months
    return schemas.ForecastOut(
        starting_balance=Decimal(account.balance), monthly_net=net, months=payload.months,
        projected_balance=projected,
        assumptions=[
            "Income and expenses stay constant each month.",
            "No interest, fees, inflation, tax, investment return, or unexpected events are included.",
            "This is a simple educational projection, not financial advice."
        ]
    )
