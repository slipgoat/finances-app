import datetime
from enum import Enum
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator


class Currency(Enum):
    EUR = 0
    USD = 1
    RUB = 2


class CategoryType(Enum):
    INCOME = 1
    ACCOUNT = 2
    EXPENSE = 3


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int


class UserBase(BaseModel):
    login: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class SettingsBase(BaseModel):
    start_date: datetime.date = datetime.date.today()
    base_currency: str = Currency.EUR.value


class SettingsCreate(SettingsBase):
    pass


class SettingsUpdate(SettingsBase):
    user_id: int

    class Config:
        orm_mode = True


class Settings(SettingsBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class CategoryBase(BaseModel):
    name: str
    type: int
    amount: float = 0.0
    currency: int = Currency.EUR.value


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: Optional[str]
    type: Optional[int]
    amount: Optional[float]
    currency: Optional[int]


class Category(CategoryBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class TransactionBase(BaseModel):
    amount: float
    source: int
    destination: int
    timestamp: datetime.datetime

    @validator('amount')
    def amount_great_than_zero(cls, v):
        if v < 0:
            raise HTTPException(status_code=400, detail="amount should not be negative")
        return v

    @validator('destination')
    def destination_not_equal_source(cls, v, values):
        if "source" in values and v == values["source"]:
            raise HTTPException(status_code=400, detail="destination should not be equal to source")
        return v


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(TransactionBase):
    amount: Optional[float]
    source: Optional[int]
    destination: Optional[int]
    timestamp: Optional[datetime.datetime]


class Transaction(TransactionBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
