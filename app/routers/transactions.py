from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db import get_db
from app import models
from app.schemas import TransactionCreate, TransactionOut

router = APIRouter()


@router.post("/", response_model=TransactionOut)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
	user = db.query(models.User).get(payload.user_id)
	merchant = db.query(models.Merchant).get(payload.merchant_id)
	if not user or not merchant:
		raise HTTPException(status_code=404, detail="User or merchant not found")
	if user.wallet_balance < payload.amount:
		raise HTTPException(status_code=400, detail="Insufficient balance")
	user.wallet_balance -= payload.amount
	txn = models.Transaction(
		user_id=user.id,
		merchant_id=merchant.id,
		amount=payload.amount,
		status="SUCCESS",
	)
	db.add(txn)
	db.add(user)
	db.commit()
	db.refresh(txn)
	return txn


@router.get("/", response_model=list[TransactionOut])
def list_transactions(user_id: Optional[int] = None, db: Session = Depends(get_db)):
	query = db.query(models.Transaction)
	if user_id is not None:
		query = query.filter(models.Transaction.user_id == user_id)
	return query.order_by(models.Transaction.created_at.desc()).all() 