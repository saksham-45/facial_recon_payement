"""
FacePay Production Application
High-performance face recognition payment system
Started: July 2023
Author: Saksham
Version: 2.0.0 - Production-grade with WebSocket and advanced ML
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import uuid
import asyncio

from app.routers import health, users, merchants, transactions, webcam
from app.services.websocket_service import websocket_manager
from app.db import Base, engine

app = FastAPI(title="FacePay Production", version="2.0.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/frontend", StaticFiles(directory="frontend/build", html=True), name="frontend")

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
	return {
		"message": "FacePay Production API", 
		"version": "2.0.0", 
		"features": [
			"user_management", 
			"payment_simulation", 
			"webcam_integration",
			"websocket_realtime",
			"advanced_face_recognition",
			"react_frontend"
		],
		"endpoints": {
			"api_docs": "/docs",
			"frontend": "/frontend",
			"websocket": "/ws/face-recognition"
		}
	}

@app.websocket("/ws/face-recognition")
async def websocket_endpoint(websocket: WebSocket):
	"""WebSocket endpoint for real-time face recognition"""
	client_id = str(uuid.uuid4())
	await websocket_manager.connect(websocket, client_id)
	
	try:
		while True:
			data = await websocket.receive_text()
			message = json.loads(data)
			
			if message["type"] == "video_frame":
				await websocket_manager.process_video_frame(client_id, message["frame_data"])
			elif message["type"] == "toggle_face_detection":
				await websocket_manager.toggle_face_detection(client_id, message["enabled"])
			elif message["type"] == "match_face":
				await websocket_manager.match_face(client_id, message["embedding"])
			elif message["type"] == "clear_face_cache":
				await websocket_manager.clear_face_cache(client_id)
				
	except WebSocketDisconnect:
		websocket_manager.disconnect(client_id)
	except Exception as e:
		print(f"WebSocket error: {e}")
		websocket_manager.disconnect(client_id)

@app.get("/demo")
def demo_page():
	"""Redirect to the React frontend"""
	return {"frontend_url": "/frontend", "api_docs": "/docs"} 