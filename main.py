from fastapi import FastAPI, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session

import database_crud
import service
from auth import verify_token

from database import SessionLocal, Base, engine
from models import CategoryCreate, Category, TransactionCreate, Transaction, CategoryUpdate, TransactionUpdate, \
    Settings, SettingsUpdate, User, Token

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
v1 = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
    finally:
        db.close()


@v1.get("/state")
async def root(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = verify_token(db, token)
    incomes = database_crud.get_incomes(db, user_id)
    accounts = database_crud.get_accounts(db, user_id)
    expenses = database_crud.get_expenses(db, user_id)
    return {
        "state": {
            "user": database_crud.get_user(db, user_id),
            "settings": database_crud.get_user_settings(db, user_id),
            "incomes": incomes,
            "accounts": accounts,
            "expenses": expenses,
            "transactions": database_crud.get_transactions(db, user_id)
        }
    }


@v1.post("/signup", response_model=Token)
async def signup(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    return service.signup(db, data)


@v1.post("/signin", response_model=Token)
async def signin(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    return service.signin(db, data)


@v1.get("/users", response_model=list[User])
async def get_users(db: Session = Depends(get_db)):
    return database_crud.get_users(db)


@v1.get("/settings", response_model=Settings)
async def get_user_settings(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return service.get_user_settings(db, token)


@v1.patch("/settings", response_model=Settings)
async def update_user_settings(
        settings_update: SettingsUpdate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    return service.update_user_settings(db, settings_update, token)


@v1.get("/incomes", response_model=list[Category])
async def get_incomes(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return service.get_incomes(db, token)


@v1.get("/accounts", response_model=list[Category])
async def get_accounts(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return service.get_accounts(db, token)


@v1.get("/expenses", response_model=list[Category])
async def get_expenses(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return service.get_expenses(db, token)


@v1.get("/categories/{category_id}", response_model=Category)
async def get_category(category_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return service.get_category(db, category_id, token)


@v1.post("/categories", response_model=Category)
async def add_category(
        category_create: CategoryCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    return service.add_category(db, category_create, token)


@v1.patch("/categories/{category_id}", response_model=Category)
async def update_category(
        category_update: CategoryUpdate,
        category_id: int,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)):
    return service.update_category(db, category_update, category_id, token)


@v1.delete("/categories/{category_id}", status_code=204)
async def delete_category(category_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return service.delete_category(db, category_id, token)


@v1.post("/income-account-transactions", response_model=Transaction)
async def add_income_account_transaction(
        transaction_create: TransactionCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    return service.add_income_account_transaction(db, transaction_create, token)


@v1.post("/account-expense-transactions", response_model=Transaction)
async def add_account_expense_transaction(
        transaction_create: TransactionCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    return service.add_account_expense_transaction(db, transaction_create, token)


@v1.get("/categories/{category_id}/transactions", response_model=list[Transaction])
async def get_category_transactions(category_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return service.get_category_transactions(db, category_id, token)


@v1.patch("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction(
        transaction_update: TransactionUpdate,
        transaction_id: int,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    return service.update_transaction(db, transaction_update, transaction_id, token)


@v1.delete("/transactions/{transaction_id}", status_code=204)
async def delete_transaction(transaction_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return service.delete_transaction(db, transaction_id, token)


app.mount("/api/v1", v1)
