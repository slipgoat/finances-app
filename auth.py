import json

from fastapi import HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import validation
import database_crud
from app_settings import AppSettings

from models import TokenData

SECRET_KEY = AppSettings().secret_key
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(password: str, hashed_password: str):
    if not pwd_context.verify(password, hashed_password):
        raise HTTPException(status_code=401, detail="unauthorized")


def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)


def create_token(data: dict) -> str:
    payload = {
        "sub": json.dumps(data)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(db: Session, token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data: TokenData = TokenData(**json.loads(payload["sub"]))
        user = database_crud.get_user(db, token_data.user_id)
        validation.validate_entity_exists(token_data.user_id, "user", user, 401)
        return token_data.user_id
    except JWTError as error:
        raise HTTPException(status_code=401, detail=f"unauthorized: {error}")

