"""
WebSocket Service for Real-time Face Recognition
Handles live video streaming and face detection
"""

import asyncio
import json
import base64
import cv2
import numpy as np
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import structlog
from .face_recognition import face_service

logger = structlog.get_logger()

class WebSocketManager:
    """Manages WebSocket connections for real-time face recognition"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.face_detection_enabled: Dict[str, bool] = {}
        self.face_embeddings_cache: Dict[str, List[np.ndarray]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.face_detection_enabled[client_id] = False
        self.face_embeddings_cache[client_id] = []
        
        logger.info("WebSocket connected", client_id=client_id)
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "client_id": client_id,
            "message": "Connected to FacePay real-time service"
        }, client_id)
    
    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.face_detection_enabled:
            del self.face_detection_enabled[client_id]
        if client_id in self.face_embeddings_cache:
            del self.face_embeddings_cache[client_id]
        
        logger.info("WebSocket disconnected", client_id=client_id)
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error("Error sending message", client_id=client_id, error=str(e))
    
    async def broadcast_message(self, message: dict):
        """Broadcast message to all connected clients"""
        for client_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, client_id)
    
    async def process_video_frame(self, client_id: str, frame_data: str):
        """Process incoming video frame for face detection"""
        try:
            # Decode base64 frame
            frame_bytes = base64.b64decode(frame_data)
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                await self.send_personal_message({
                    "type": "error",
                    "message": "Failed to decode frame"
                }, client_id)
                return
            
            # Process frame for face detection
            if self.face_detection_enabled.get(client_id, False):
                result = await face_service.process_image_async(frame)
                
                # Send face detection results
                await self.send_personal_message({
                    "type": "face_detection_result",
                    "faces_detected": result['face_count'],
                    "faces": [
                        {
                            "bbox": face['bbox'],
                            "confidence": float(face['confidence']),
                            "has_embedding": 'embedding' in face
                        }
                        for face in result['faces']
                    ],
                    "embeddings_count": len(result['embeddings'])
                }, client_id)
                
                # Store embeddings for matching
                if result['embeddings']:
                    self.face_embeddings_cache[client_id].extend(result['embeddings'])
                    # Keep only last 10 embeddings to prevent memory issues
                    if len(self.face_embeddings_cache[client_id]) > 10:
                        self.face_embeddings_cache[client_id] = self.face_embeddings_cache[client_id][-10:]
            
        except Exception as e:
            logger.error("Error processing video frame", client_id=client_id, error=str(e))
            await self.send_personal_message({
                "type": "error",
                "message": f"Frame processing error: {str(e)}"
            }, client_id)
    
    async def toggle_face_detection(self, client_id: str, enabled: bool):
        """Toggle face detection for a client"""
        self.face_detection_enabled[client_id] = enabled
        await self.send_personal_message({
            "type": "face_detection_toggled",
            "enabled": enabled
        }, client_id)
        
        logger.info("Face detection toggled", client_id=client_id, enabled=enabled)
    
    async def match_face(self, client_id: str, query_embedding: List[float]):
        """Match face against stored embeddings"""
        try:
            query_np = np.array(query_embedding)
            stored_embeddings = self.face_embeddings_cache.get(client_id, [])
            
            if not stored_embeddings:
                await self.send_personal_message({
                    "type": "face_match_result",
                    "match_found": False,
                    "message": "No stored faces to match against"
                }, client_id)
                return
            
            # Find best match
            best_match_index = face_service.find_best_match(query_np, stored_embeddings, threshold=0.6)
            
            if best_match_index is not None:
                await self.send_personal_message({
                    "type": "face_match_result",
                    "match_found": True,
                    "match_index": int(best_match_index),
                    "confidence": float(face_service.calculate_similarity(
                        query_np, 
                        stored_embeddings[best_match_index]
                    ))
                }, client_id)
            else:
                await self.send_personal_message({
                    "type": "face_match_result",
                    "match_found": False,
                    "message": "No matching face found"
                }, client_id)
                
        except Exception as e:
            logger.error("Error matching face", client_id=client_id, error=str(e))
            await self.send_personal_message({
                "type": "error",
                "message": f"Face matching error: {str(e)}"
            }, client_id)
    
    async def clear_face_cache(self, client_id: str):
        """Clear stored face embeddings for a client"""
        self.face_embeddings_cache[client_id] = []
        await self.send_personal_message({
            "type": "face_cache_cleared",
            "message": "Face cache cleared"
        }, client_id)
        
        logger.info("Face cache cleared", client_id=client_id)

# Global WebSocket manager
websocket_manager = WebSocketManager()
