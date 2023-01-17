from datetime import datetime

from sqlalchemy.orm import Session

from database_models import UserDb, CategoryDb, TransactionDb, SettingsDb
from models import UserCreate, CategoryType, CategoryCreate, TransactionCreate, CategoryUpdate, TransactionUpdate, \
    SettingsCreate, SettingsUpdate, Currency


def get_users(db: Session, offset: int = 0, limit: int = 100) -> list[UserDb]:
    return db.query(UserDb).offset(offset).limit(limit).all()


def get_user(db: Session, user_id: int) -> UserDb:
    return db.query(UserDb).filter(UserDb.id == user_id).first()


def get_user_by_login(db: Session, login: str) -> UserDb:
    return db.query(UserDb).filter(UserDb.login == login).first()


def create_user(db: Session, user_create: UserCreate) -> UserDb:
    fake_hashed_password = user_create.password
    db_user = UserDb(login=user_create.login, password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    settings_create = SettingsCreate(start_date=datetime.utcnow(), base_currency=Currency.EUR.value)
    db_settings = SettingsDb(**settings_create.dict(), user_id=db_user.id)
    db.add(db_settings)

    db.commit()
    return db_user


def get_user_settings(db: Session, user_id: int) -> SettingsDb:
    return db.query(SettingsDb).filter(SettingsDb.user_id == user_id).first()


def update_user_settings(db: Session, settings_update: SettingsUpdate, user_id: int) -> SettingsDb:
    db.query(SettingsDb).filter(SettingsDb.user_id == user_id).update(settings_update.dict(exclude_none=True))
    db.commit()
    return db.query(SettingsDb).filter(SettingsDb.user_id == user_id).first()


def get_incomes(db: Session, user_id: int, offset: int = 0, limit: int = 100) -> list[CategoryDb]:
    return db.query(CategoryDb) \
        .filter(CategoryDb.user_id == user_id) \
        .filter(CategoryDb.type == CategoryType.INCOME.value) \
        .offset(offset).limit(limit).all()


def get_accounts(db: Session, user_id: int, offset: int = 0, limit: int = 100) -> list[CategoryDb]:
    return db.query(CategoryDb) \
        .filter(CategoryDb.user_id == user_id) \
        .filter(CategoryDb.type == CategoryType.ACCOUNT.value) \
        .offset(offset).limit(limit).all()


def get_expenses(db: Session, user_id: int, offset: int = 0, limit: int = 100) -> list[CategoryDb]:
    return db.query(CategoryDb) \
        .filter(CategoryDb.user_id == user_id) \
        .filter(CategoryDb.type == CategoryType.EXPENSE.value) \
        .offset(offset).limit(limit).all()


def get_category_by_id(db: Session, category_id: int) -> CategoryDb:
    return db.query(CategoryDb).filter(CategoryDb.id == category_id).first()


def get_category_ids(db: Session, ids: list[int]) -> list[int]:
    return list(map(lambda category: category.id, db.query(CategoryDb).filter(CategoryDb.id.in_(ids)).all()))


def create_category(db: Session, category_create: CategoryCreate, user_id: int) -> CategoryDb:
    db_category = CategoryDb(**category_create.dict(), user_id=user_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_update: CategoryUpdate, category_id: int) -> CategoryDb:
    db.query(CategoryDb).filter(CategoryDb.id == category_id).update(category_update.dict(exclude_none=True))
    db.commit()

    return db.query(CategoryDb).filter(CategoryDb.id == category_id).first()


def delete_category(db: Session, category_id: int):
    db.query(CategoryDb).filter(CategoryDb.id == category_id).delete()
    transactions = get_transaction_by_category_id(db, category_id)

    for transaction in transactions:
        delete_transaction(db, transaction.id)

    db.commit()


def get_transactions(db: Session, user_id: int, offset: int = 0, limit: int = 100) -> list[TransactionDb]:
    return db.query(TransactionDb) \
        .filter(TransactionDb.user_id == user_id) \
        .offset(offset).limit(limit).all()


def get_transaction_by_id(db: Session, transaction_id: int) -> TransactionDb:
    return db.query(TransactionDb).filter(TransactionDb.id == transaction_id).first()


def get_transaction_by_category_id(db: Session, category_id: int) -> list[TransactionDb]:
    source_transactions = db.query(TransactionDb).filter(TransactionDb.source == category_id).all()
    destination_transactions = db.query(TransactionDb).filter(TransactionDb.destination == category_id).all()
    output = [*source_transactions, *destination_transactions]
    output.sort(key=lambda transaction: transaction.timestamp, reverse=True)
    return output


def create_transaction(db: Session, transaction_create: TransactionCreate, user_id: int) -> TransactionDb:
    db_transaction = TransactionDb(**transaction_create.dict(), user_id=user_id)
    db.add(db_transaction)
    db.query(CategoryDb) \
        .filter(CategoryDb.id == transaction_create.source) \
        .update({"amount": CategoryDb.amount - transaction_create.amount})
    db.query(CategoryDb) \
        .filter(CategoryDb.id == transaction_create.destination) \
        .update({"amount": CategoryDb.amount + transaction_create.amount})

    db.commit()
    db.refresh(db_transaction)

    return db_transaction


def update_transaction(db: Session, transaction_update: TransactionUpdate, transaction_id: int) -> TransactionDb:
    db_transaction = db.query(TransactionDb).filter(TransactionDb.id == transaction_id).first()

    db.query(CategoryDb) \
        .filter(CategoryDb.id == db_transaction.source) \
        .update({"amount": CategoryDb.amount + db_transaction.amount})
    db.query(CategoryDb) \
        .filter(CategoryDb.id == transaction_update.source) \
        .update({"amount": CategoryDb.amount - transaction_update.amount})
    db.query(CategoryDb) \
        .filter(CategoryDb.id == db_transaction.destination) \
        .update({"amount": CategoryDb.amount - db_transaction.amount})
    db.query(CategoryDb) \
        .filter(CategoryDb.id == transaction_update.destination) \
        .update({"amount": CategoryDb.amount + transaction_update.amount})

    db.query(TransactionDb).filter(TransactionDb.id == transaction_id)\
        .update(transaction_update.dict(exclude_none=True))

    db.commit()
    db.refresh(db_transaction)

    return db_transaction


def delete_transaction(db: Session, transaction_id: int, commit: bool = True):
    db_transaction = db.query(TransactionDb).filter(TransactionDb.id == transaction_id).first()

    db.query(CategoryDb) \
        .filter(CategoryDb.id == db_transaction.source) \
        .update({"amount": CategoryDb.amount + db_transaction.amount})
    db.query(CategoryDb) \
        .filter(CategoryDb.id == db_transaction.destination) \
        .update({"amount": CategoryDb.amount - db_transaction.amount})

    db.query(TransactionDb).filter(TransactionDb.id == transaction_id).delete()

    if commit:
        db.commit()
