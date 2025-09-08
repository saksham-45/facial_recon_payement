import React, { useRef, useEffect, useState, useCallback } from 'react';
import styled from 'styled-components';
import { Camera, User, CheckCircle, XCircle, Loader } from 'lucide-react';
import toast from 'react-hot-toast';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  color: white;
`;

const VideoContainer = styled.div`
  position: relative;
  width: 100%;
  max-width: 640px;
  height: 480px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  background: #000;
`;

const Video = styled.video`
  width: 100%;
  height: 100%;
  object-fit: cover;
`;

const Canvas = styled.canvas`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
`;

const Controls = styled.div`
  display: flex;
  gap: 1rem;
  margin: 2rem 0;
  flex-wrap: wrap;
  justify-content: center;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' | 'success' | 'danger' }>`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  border: none;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: ${props => {
    switch (props.variant) {
      case 'success': return 'linear-gradient(45deg, #4CAF50, #45a049)';
      case 'danger': return 'linear-gradient(45deg, #f44336, #da190b)';
      case 'secondary': return 'linear-gradient(45deg, #6c757d, #5a6268)';
      default: return 'linear-gradient(45deg, #ff6b6b, #ee5a24)';
    }
  }};
  color: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const StatusCard = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 1.5rem;
  margin: 1rem 0;
  min-width: 300px;
  text-align: center;
`;

const FaceBox = styled.div<{ x: number; y: number; width: number; height: number }>`
  position: absolute;
  left: ${props => props.x}px;
  top: ${props => props.y}px;
  width: ${props => props.width}px;
  height: ${props => props.height}px;
  border: 3px solid #4CAF50;
  border-radius: 8px;
  background: rgba(76, 175, 80, 0.1);
  pointer-events: none;
`;

interface FaceDetectionResult {
  faces_detected: number;
  faces: Array<{
    bbox: [number, number, number, number];
    confidence: number;
    has_embedding: boolean;
  }>;
  embeddings_count: number;
}

interface FaceRecognitionProps {
  onFaceDetected?: (faces: FaceDetectionResult) => void;
  onFaceMatched?: (matchResult: any) => void;
}

const FaceRecognition: React.FC<FaceRecognitionProps> = ({ 
  onFaceDetected, 
  onFaceMatched 
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const animationRef = useRef<number>();

  const [isConnected, setIsConnected] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [faces, setFaces] = useState<FaceDetectionResult['faces']>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Initialize WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket('ws://localhost:8000/ws/face-recognition');
      
      ws.onopen = () => {
        setIsConnected(true);
        toast.success('Connected to FacePay service');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
          case 'face_detection_result':
            setFaces(data.faces);
            onFaceDetected?.(data);
            break;
          case 'face_match_result':
            onFaceMatched?.(data);
            break;
          case 'error':
            toast.error(data.message);
            break;
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        toast.error('Disconnected from FacePay service');
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        toast.error('WebSocket connection error');
      };

      wsRef.current = ws;
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [onFaceDetected, onFaceMatched]);

  // Initialize camera
  const initializeCamera = useCallback(async () => {
    try {
      setIsLoading(true);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        }
      });
      
      streamRef.current = stream;
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      
      toast.success('Camera initialized');
    } catch (error) {
      console.error('Camera error:', error);
      toast.error('Failed to access camera');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Start face detection
  const startDetection = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      toast.error('WebSocket not connected');
      return;
    }

    setIsDetecting(true);
    wsRef.current.send(JSON.stringify({
      type: 'toggle_face_detection',
      enabled: true
    }));

    // Start sending video frames
    const sendFrame = () => {
      if (videoRef.current && wsRef.current && isDetecting) {
        const canvas = canvasRef.current;
        if (canvas) {
          const ctx = canvas.getContext('2d');
          if (ctx) {
            canvas.width = videoRef.current.videoWidth;
            canvas.height = videoRef.current.videoHeight;
            ctx.drawImage(videoRef.current, 0, 0);
            
            const frameData = canvas.toDataURL('image/jpeg', 0.8);
            const base64Data = frameData.split(',')[1];
            
            wsRef.current.send(JSON.stringify({
              type: 'video_frame',
              frame_data: base64Data
            }));
          }
        }
        animationRef.current = requestAnimationFrame(sendFrame);
      }
    };

    sendFrame();
  }, [isDetecting]);

  // Stop face detection
  const stopDetection = useCallback(() => {
    setIsDetecting(false);
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({
        type: 'toggle_face_detection',
        enabled: false
      }));
    }
  }, []);

  // Clear face cache
  const clearCache = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({
        type: 'clear_face_cache'
      }));
    }
    setFaces([]);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <Container>
      <h1>🎥 FacePay Real-time Recognition</h1>
      
      <VideoContainer>
        <Video
          ref={videoRef}
          autoPlay
          muted
          playsInline
        />
        <Canvas ref={canvasRef} />
        {faces.map((face, index) => (
          <FaceBox
            key={index}
            x={face.bbox[0]}
            y={face.bbox[1]}
            width={face.bbox[2]}
            height={face.bbox[3]}
          />
        ))}
      </VideoContainer>

      <Controls>
        <Button
          onClick={initializeCamera}
          disabled={isLoading}
        >
          {isLoading ? <Loader size={20} /> : <Camera size={20} />}
          {isLoading ? 'Initializing...' : 'Start Camera'}
        </Button>

        <Button
          onClick={isDetecting ? stopDetection : startDetection}
          disabled={!isConnected || isLoading}
          variant={isDetecting ? 'danger' : 'success'}
        >
          {isDetecting ? <XCircle size={20} /> : <CheckCircle size={20} />}
          {isDetecting ? 'Stop Detection' : 'Start Detection'}
        </Button>

        <Button
          onClick={clearCache}
          variant="secondary"
        >
          <User size={20} />
          Clear Cache
        </Button>
      </Controls>

      <StatusCard>
        <h3>Status</h3>
        <p>WebSocket: {isConnected ? '✅ Connected' : '❌ Disconnected'}</p>
        <p>Camera: {streamRef.current ? '✅ Active' : '❌ Inactive'}</p>
        <p>Detection: {isDetecting ? '✅ Running' : '❌ Stopped'}</p>
        <p>Faces Detected: {faces.length}</p>
      </StatusCard>
    </Container>
  );
};

export default FaceRecognition;
