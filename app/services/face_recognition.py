"""
High-Performance Face Recognition Service
Uses MediaPipe for detection and FaceNet for embeddings
"""

import cv2
import numpy as np
import mediapipe as mp
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from typing import List, Tuple, Optional, Dict
import asyncio
from concurrent.futures import ThreadPoolExecutor
import structlog

logger = structlog.get_logger()

class FaceRecognitionService:
    """High-performance face recognition using MediaPipe + FaceNet"""
    
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 0 for 2m range, 1 for 5m range
            min_detection_confidence=0.5
        )
        
        # Initialize FaceNet model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.mtcnn = MTCNN(
            image_size=160,
            margin=0,
            min_face_size=20,
            thresholds=[0.6, 0.7, 0.7],
            factor=0.709,
            post_process=False,
            device=self.device
        )
        self.facenet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        
        # Thread pool for async processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("Face recognition service initialized", device=str(self.device))
    
    async def detect_faces_async(self, image: np.ndarray) -> List[Dict]:
        """Detect faces in image asynchronously using MediaPipe"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self._detect_faces_sync, 
            image
        )
    
    def _detect_faces_sync(self, image: np.ndarray) -> List[Dict]:
        """Synchronous face detection using MediaPipe"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_image)
        
        faces = []
        if results.detections:
            h, w, _ = image.shape
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                confidence = detection.score[0]
                
                faces.append({
                    'bbox': (x, y, width, height),
                    'confidence': confidence,
                    'landmarks': None  # MediaPipe doesn't provide landmarks in basic detection
                })
        
        return faces
    
    async def extract_embedding_async(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """Extract face embedding asynchronously using FaceNet"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._extract_embedding_sync,
            image,
            bbox
        )
    
    def _extract_embedding_sync(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """Extract face embedding using FaceNet"""
        try:
            x, y, w, h = bbox
            # Extract face region
            face_crop = image[y:y+h, x:x+w]
            
            if face_crop.size == 0:
                return None
            
            # Convert to PIL Image for MTCNN
            from PIL import Image
            face_pil = Image.fromarray(cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB))
            
            # Extract face tensor
            face_tensor = self.mtcnn(face_pil)
            if face_tensor is None:
                return None
            
            # Get embedding
            with torch.no_grad():
                embedding = self.facenet(face_tensor.unsqueeze(0).to(self.device))
                return embedding.cpu().numpy().flatten()
                
        except Exception as e:
            logger.error("Error extracting embedding", error=str(e))
            return None
    
    async def process_image_async(self, image: np.ndarray) -> Dict:
        """Process image for face detection and embedding extraction"""
        # Detect faces
        faces = await self.detect_faces_async(image)
        
        # Extract embeddings for each face
        embeddings = []
        for face in faces:
            embedding = await self.extract_embedding_async(image, face['bbox'])
            if embedding is not None:
                face['embedding'] = embedding
                embeddings.append(embedding)
        
        return {
            'faces': faces,
            'embeddings': embeddings,
            'face_count': len(faces)
        }
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        # Normalize embeddings
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)
    
    def find_best_match(self, query_embedding: np.ndarray, stored_embeddings: List[np.ndarray], threshold: float = 0.6) -> Optional[int]:
        """Find best matching face from stored embeddings"""
        if not stored_embeddings:
            return None
        
        best_similarity = -1
        best_index = None
        
        for i, stored_embedding in enumerate(stored_embeddings):
            similarity = self.calculate_similarity(query_embedding, stored_embedding)
            if similarity > threshold and similarity > best_similarity:
                best_similarity = similarity
                best_index = i
        
        return best_index if best_similarity > threshold else None
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
        logger.info("Face recognition service cleaned up")

# Global instance
face_service = FaceRecognitionService()
