from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db import get_db
from app import models
from app.schemas import UserCreate, UserOut

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pin(pin: str) -> str:
	return pwd_context.hash(pin)


@router.post("/", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
	if db.query(models.User).filter(models.User.email == payload.email).first():
		raise HTTPException(status_code=400, detail="Email already registered")
	pin_hash = hash_pin(payload.pin) if payload.pin else None
	user = models.User(
		name=payload.name,
		email=payload.email,
		wallet_balance=payload.initial_balance,
		pin_hash=pin_hash,
	)
	db.add(user)
	db.commit()
	db.refresh(user)
	return user


@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
	return db.query(models.User).all() 