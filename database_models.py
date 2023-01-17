from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship

from database import Base


class UserDb(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    settings = relationship("SettingsDb", back_populates="user")
    categories = relationship("CategoryDb", back_populates="user")
    transactions = relationship("TransactionDb", back_populates="user")


class SettingsDb(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date, nullable=False)
    base_currency = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("UserDb", back_populates="settings")


class CategoryDb(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("UserDb", back_populates="categories")


class TransactionDb(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    source = Column(Integer, nullable=False)
    destination = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, nullable=False)

    user = relationship("UserDb", back_populates="transactions")
