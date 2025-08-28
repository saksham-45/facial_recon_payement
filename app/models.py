from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db import Base


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable=False)
	email = Column(String, unique=True, index=True, nullable=False)
	wallet_balance = Column(Float, default=0.0)
	face_embedding = Column(String, nullable=True)  # store as JSON string for now
	pin_hash = Column(String, nullable=True)

	transactions = relationship("Transaction", back_populates="user")


class Merchant(Base):
	__tablename__ = "merchants"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, unique=True, nullable=False)

	transactions = relationship("Transaction", back_populates="merchant")


class Transaction(Base):
	__tablename__ = "transactions"

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
	amount = Column(Float, nullable=False)
	status = Column(String, default="SUCCESS")
	created_at = Column(DateTime, default=datetime.utcnow)

	user = relationship("User", back_populates="transactions")
	merchant = relationship("Merchant", back_populates="transactions") 