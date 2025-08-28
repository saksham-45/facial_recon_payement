from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app import models
from app.schemas import MerchantCreate, MerchantOut

router = APIRouter()


@router.post("/", response_model=MerchantOut)
def create_merchant(payload: MerchantCreate, db: Session = Depends(get_db)):
	if db.query(models.Merchant).filter(models.Merchant.name == payload.name).first():
		raise HTTPException(status_code=400, detail="Merchant already exists")
	merchant = models.Merchant(name=payload.name)
	db.add(merchant)
	db.commit()
	db.refresh(merchant)
	return merchant


@router.get("/", response_model=list[MerchantOut])
def list_merchants(db: Session = Depends(get_db)):
	return db.query(models.Merchant).all() 