"""
FacePay Prototype - Main Application
Started: July 2023
Author: Saksham
Version: 0.1.2 - Added webcam integration for face capture
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import health, users, merchants, transactions, webcam
from app.db import Base, engine

app = FastAPI(title="FacePay Prototype", version="0.1.2")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def on_startup():
	Base.metadata.create_all(bind=engine)

app.include_router(health.router, prefix="/health", tags=["health"]) 
app.include_router(users.router, prefix="/users", tags=["users"]) 
app.include_router(merchants.router, prefix="/merchants", tags=["merchants"]) 
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"]) 
app.include_router(webcam.router, prefix="/webcam", tags=["webcam"])

@app.get("/")
def root():
	return {"message": "FacePay API is running", "version": "0.1.2", "features": ["user_management", "payment_simulation", "webcam_integration"]}

@app.get("/demo")
def demo_page():
	"""Redirect to the webcam demo page"""
	return {"demo_url": "/static/index.html"} 