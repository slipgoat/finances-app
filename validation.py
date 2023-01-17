from typing import Any

from fastapi import HTTPException

from database_models import CategoryDb, TransactionDb, UserDb
from models import CategoryType


def validate_none_value(value: any, entity_name: str, status_code: int = 404):
    if value is None:
        raise HTTPException(status_code=status_code, detail=f"{entity_name} is not presented")


def validate_entity_exists(entity_id: int, entity_name: str, value: Any, status_code: int = 404):
    if value is None:
        raise HTTPException(status_code=status_code, detail=f"{entity_name} {entity_id} is not found")


def validate_entity_exists_in_list(
        entity_id: int,
        entity_name: str,
        value: Any,
        value_list: list[Any],
        status_code: int = 404
):
    if value not in value_list:
        raise HTTPException(status_code=status_code, detail=f"{entity_name} {entity_id} is not found")


def validate_login_exists(login: str, user: UserDb):
    if user is not None:
        raise HTTPException(status_code=400, detail=f"user {login} is already registered")


def validate_login_is_not_existed(user: UserDb):
    if user is None:
        raise HTTPException(status_code=401, detail=f"unauthorized")


def validate_not_changing_category_type(new_category_type: int, category_type: int):
    if new_category_type is not None:
        if new_category_type != category_type:
            raise HTTPException(status_code=400, detail="category type can not be changed")


def validate_source_destination_exist(source: int, destination: int, categories_id: list[int]):
    validate_entity_exists_in_list(source, 'source', source, categories_id)
    validate_entity_exists_in_list(destination, 'source', destination, categories_id)


def validate_income_account_source_type(category_type):
    if category_type != CategoryType.INCOME.value:
        raise HTTPException(status_code=400, detail="source should be income")


def validate_income_account_destination_type(category_type):
    if category_type != CategoryType.ACCOUNT.value:
        raise HTTPException(status_code=400, detail="destination should be account")


def validate_account_expense_source_type(category_type):
    if category_type != CategoryType.ACCOUNT.value:
        raise HTTPException(status_code=400, detail="source should be account")


def validate_account_expense_destination_type(category_type):
    if category_type != CategoryType.ACCOUNT.value and category_type != CategoryType.EXPENSE.value:
        raise HTTPException(status_code=400, detail="destination should be account or expense")
