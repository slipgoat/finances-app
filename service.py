from datetime import date

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import database_crud
from database_models import TransactionDb, CategoryDb, SettingsDb
from models import TransactionCreate, CategoryUpdate, TransactionUpdate, UserCreate, SettingsUpdate, TokenData, \
    CategoryCreate, Token
import validation
import auth


def signup(db: Session, data: OAuth2PasswordRequestForm) -> Token:
    validation.validate_login_exists(data.username, database_crud.get_user_by_login(db, data.username))
    hashed_password = auth.get_hashed_password(data.password)
    user_create_hashed = UserCreate(login=data.username, password=hashed_password)
    user = database_crud.create_user(db, user_create_hashed)

    token = auth.create_token(TokenData(user_id=user.id).dict())
    return Token(access_token=token)


def signin(db: Session, data: OAuth2PasswordRequestForm) -> Token:
    user = database_crud.get_user_by_login(db, data.username)
    validation.validate_login_is_not_existed(user)
    auth.verify_password(data.password, user.password)

    token = auth.create_token(TokenData(user_id=user.id).dict())
    return Token(access_token=token)


def get_user_settings(db: Session, token: str) -> SettingsDb:
    user_id = auth.verify_token(db, token)
    return database_crud.get_user_settings(db, user_id)


def update_user_settings(db: Session, settings_update: SettingsUpdate, token: str) -> SettingsDb:
    user_id = auth.verify_token(db, token)
    return database_crud.update_user_settings(db, settings_update, user_id)


def get_incomes(db: Session, token: str) -> list[CategoryDb]:
    user_id = auth.verify_token(db, token)
    return database_crud.get_incomes(db, user_id)


def get_accounts(db: Session, token: str) -> list[CategoryDb]:
    user_id = auth.verify_token(db, token)
    return database_crud.get_accounts(db, user_id)


def get_expenses(db: Session, token: str) -> list[CategoryDb]:
    user_id = auth.verify_token(db, token)
    return database_crud.get_expenses(db, user_id)


def get_category(db: Session, category_id: int, token: str) -> CategoryDb:
    auth.verify_token(db, token)
    category = database_crud.get_category_by_id(db, category_id)
    validation.validate_entity_exists(category_id, "category", category)
    return category


def add_category(db: Session, category_create: CategoryCreate, token: str) -> CategoryDb:
    user_id = auth.verify_token(db, token)
    return database_crud.create_category(db, category_create, user_id)


def update_category(db: Session, category_update: CategoryUpdate, category_id: int, token: str) -> CategoryDb:
    auth.verify_token(db, token)
    validation.validate_entity_exists(category_id, "category", database_crud.get_category_by_id(db, category_id))
    validation.validate_not_changing_category_type(
        category_update.type, database_crud.get_category_by_id(db, category_id).type
    )
    return database_crud.update_category(db, category_update, category_id)


def delete_category(db: Session, category_id: int, token: str):
    auth.verify_token(db, token)
    validation.validate_entity_exists(category_id, "category", database_crud.get_category_by_id(db, category_id))
    return database_crud.delete_category(db, category_id)


def add_income_account_transaction(
        db: Session,
        transaction_create: TransactionCreate,
        token: str
) -> TransactionDb:
    user_id = auth.verify_token(db, token)
    validation.validate_source_destination_exist(
        transaction_create.source,
        transaction_create.destination,
        database_crud.get_category_ids(db, [transaction_create.source, transaction_create.destination])
    )
    validation.validate_income_account_source_type(database_crud.get_category_by_id(db, transaction_create.source).type)
    validation.validate_income_account_destination_type(
        database_crud.get_category_by_id(db, transaction_create.destination).type
    )

    return database_crud.create_transaction(db, transaction_create, user_id=user_id)


def add_account_expense_transaction(
        db: Session,
        transaction_create: TransactionCreate,
        token: str
) -> TransactionDb:
    user_id = auth.verify_token(db, token)
    validation.validate_source_destination_exist(
        transaction_create.source,
        transaction_create.destination,
        database_crud.get_category_ids(db, [transaction_create.source, transaction_create.destination])
    )
    validation.validate_account_expense_source_type(
        database_crud.get_category_by_id(db, transaction_create.source).type
    )
    validation.validate_account_expense_destination_type(
        database_crud.get_category_by_id(db, transaction_create.destination).type
    )

    transaction_create.timestamp = transaction_create.timestamp
    return database_crud.create_transaction(db, transaction_create, user_id=user_id)


def get_category_transactions(
        db: Session,
        category_id: int,
        period_start: date,
        period_end: date,
        token: str
) -> list[TransactionDb]:
    auth.verify_token(db, token)
    validation.validate_entity_exists(category_id, "category", database_crud.get_category_by_id(db, category_id))
    return database_crud.get_category_transactions(db, category_id, period_start, period_end)


def get_category_period_sum(
        db: Session,
        category_id: int,
        period_start: date,
        period_end: date,
        token: str
) -> float:
    auth.verify_token(db, token)
    validation.validate_entity_exists(category_id, "category", database_crud.get_category_by_id(db, category_id))
    return database_crud.get_category_period_sum(db, category_id, period_start, period_end)


# TODO: add validation transaction direction validation
def update_transaction(
        db: Session,
        transaction_update: TransactionUpdate,
        transaction_id: int,
        token: str
) -> TransactionDb:
    auth.verify_token(db, token)
    validation.validate_entity_exists(
        transaction_id,
        "transaction", database_crud.get_transaction_by_id(db, transaction_id))
    validation.validate_source_destination_exist(
        transaction_update.source,
        transaction_update.destination,
        database_crud.get_category_ids(db, [transaction_update.source, transaction_update.destination])
    )
    return database_crud.update_transaction(db, transaction_update, transaction_id)


def delete_transaction(db: Session, transaction_id: int, token: str):
    auth.verify_token(db, token)
    validation.validate_entity_exists(
        transaction_id,
        "transaction",
        database_crud.get_transaction_by_id(db, transaction_id)
    )
    return database_crud.delete_transaction(db, transaction_id)
