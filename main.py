from fastapi import FastAPI, Depends, Header
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


def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
    finally:
        db.close()


@app.get("/state")
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


@app.post("/signup", response_model=Token)
async def signup(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    return service.signup(db, data)


@app.post("/signin", response_model=Token)
async def signin(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    return service.signin(db, data)


@app.get("/users", response_model=list[User])
async def get_users(db: Session = Depends(get_db)):
    return database_crud.get_users(db)


@app.get("/settings", response_model=Settings)
async def get_user_settings(user_id: int, db: Session = Depends(get_db)):
    return service.get_user_settings(db, user_id)


@app.patch("/settings", response_model=Settings)
async def update_user_settings(settings_update: SettingsUpdate, user_id: int = Header(), db: Session = Depends(get_db)):
    return service.update_user_settings(db, settings_update, user_id)


@app.get("/incomes", response_model=list[Category])
async def get_incomes(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return service.get_incomes(db, token)


@app.get("/accounts", response_model=list[Category])
async def get_accounts(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return service.get_accounts(db, token)


@app.get("/expenses", response_model=list[Category])
async def get_expenses(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return service.get_expenses(db, token)


@app.get("/categories/{category_id}", response_model=Category)
async def get_category(category_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return service.get_category(db, category_id, token)


@app.post("/categories", response_model=Category)
async def add_category(
        category_create: CategoryCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    return service.add_category(db, category_create, token)


@app.patch("/categories/{category_id}", response_model=Category)
async def update_category(
        category_update: CategoryUpdate,
        category_id: int,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)):
    return service.update_category(db, category_update, category_id, token)


@app.delete("/categories/{category_id}", status_code=204)
async def delete_category(category_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return service.delete_category(db, category_id, token)


@app.post("/income-account-transactions", response_model=Transaction)
async def add_income_account_transaction(
        transaction_create: TransactionCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    return service.add_income_account_transaction(db, transaction_create, token)


@app.post("/account-expense-transactions", response_model=Transaction)
async def add_account_expense_transaction(
        transaction_create: TransactionCreate,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    return service.add_account_expense_transaction(db, transaction_create, token)


@app.get("/categories/{category_id}/transactions", response_model=list[Transaction])
async def get_category_transactions(category_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return service.get_category_transactions(db, category_id, token)


@app.patch("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction(
        transaction_update: TransactionUpdate,
        transaction_id: int,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    return service.update_transaction(db, transaction_update, transaction_id, token)


@app.delete("/transactions/{transaction_id}", status_code=204)
async def delete_transaction(transaction_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return service.delete_transaction(db, transaction_id, token)
