"""
Webcam Integration for FacePay
Handles camera capture and face detection
"""

import cv2
import numpy as np
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import base64
from typing import Optional
import json

router = APIRouter()

def generate_frames():
    """Generate video frames from webcam"""
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise HTTPException(status_code=500, detail="Could not open camera")
    
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        camera.release()

@router.get("/stream")
def video_stream():
    """Stream webcam feed"""
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.post("/capture")
async def capture_face():
    """Capture a single frame from webcam and detect faces"""
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise HTTPException(status_code=500, detail="Could not open camera")
    
    try:
        success, frame = camera.read()
        if not success:
            raise HTTPException(status_code=500, detail="Failed to capture frame")
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Load OpenCV's face detection cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Convert frame to base64
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            raise HTTPException(status_code=500, detail="Failed to encode frame")
        
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "success": True,
            "faces_detected": len(faces),
            "frame": frame_base64,
            "face_coordinates": faces.tolist() if len(faces) > 0 else []
        }
    
    finally:
        camera.release()

@router.get("/test")
def test_camera():
    """Test if camera is accessible"""
    camera = cv2.VideoCapture(0)
    if camera.isOpened():
        camera.release()
        return {"status": "Camera accessible", "camera_working": True}
    else:
        return {"status": "Camera not accessible", "camera_working": False} 