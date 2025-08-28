from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
	name: str
	email: EmailStr
	initial_balance: float = 0.0
	pin: Optional[str] = None
	# faceImageBase64 or embedding will be added later


class UserOut(BaseModel):
	id: int
	name: str
	email: EmailStr
	wallet_balance: float

	class Config:
		from_attributes = True


class MerchantCreate(BaseModel):
	name: str


class MerchantOut(BaseModel):
	id: int
	name: str

	class Config:
		from_attributes = True


class TransactionCreate(BaseModel):
	user_id: int
	merchant_id: int
	amount: float


class TransactionOut(BaseModel):
	id: int
	user_id: int
	merchant_id: int
	amount: float
	status: str
	created_at: datetime

	class Config:
		from_attributes = True 