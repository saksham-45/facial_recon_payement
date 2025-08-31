"""
FacePay Prototype - Main Application
Started: July 2023
Author: Saksham
Version: 0.1.1 - Enhanced documentation and code structure
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, users, merchants, transactions
from app.db import Base, engine

app = FastAPI(title="FacePay Prototype", version="0.1.1")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
	Base.metadata.create_all(bind=engine)

app.include_router(health.router, prefix="/health", tags=["health"]) 
app.include_router(users.router, prefix="/users", tags=["users"]) 
app.include_router(merchants.router, prefix="/merchants", tags=["merchants"]) 
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"]) 

@app.get("/")
def root():
	return {"message": "FacePay API is running", "version": "0.1.1"} 