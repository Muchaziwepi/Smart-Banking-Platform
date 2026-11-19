from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    created_at: datetime

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AccountCreate(BaseModel):
    account_type: str = Field(default="savings", pattern="^(savings|current)$")
    currency: str = Field(default="INR", min_length=3, max_length=3)

class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    account_number: str
    account_type: str
    currency: str
    balance: Decimal
    created_at: datetime

class MoneyRequest(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    description: str = Field(default="", max_length=255)

class TransferRequest(MoneyRequest):
    destination_account_number: str = Field(min_length=5, max_length=24)

class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    account_id: int
    transaction_type: str
    amount: Decimal
    description: str
    reference: str
    created_at: datetime

class LoanCreate(BaseModel):
    requested_amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    annual_income: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    existing_monthly_debt: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    purpose: str = Field(min_length=3, max_length=120)

class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    requested_amount: Decimal
    annual_income: Decimal
    existing_monthly_debt: Decimal
    purpose: str
    status: str
    note: str
    created_at: datetime

class ForecastRequest(BaseModel):
    monthly_income: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    monthly_expenses: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    months: int = Field(default=6, ge=1, le=24)

class ForecastOut(BaseModel):
    starting_balance: Decimal
    monthly_net: Decimal
    months: int
    projected_balance: Decimal
    assumptions: list[str]
