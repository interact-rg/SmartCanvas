import React, { useRef, useEffect } from 'react';
import {
  FilesetResolver,
  FaceDetector,
  GestureRecognizer,
} from '@mediapipe/tasks-vision';

interface FaceAndGestureDetectionProps {
  setIsGivingConsent: (val: boolean) => void
}

const FaceAndGestureDetection: React.FC<FaceAndGestureDetectionProps> = ({setIsGivingConsent}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const faceDetectorRef = useRef<FaceDetector | null>(null);
  const gestureRecognizerRef = useRef<GestureRecognizer | null>(null);
  const lastUpdateTimeRef = useRef<number>(0);

  useEffect(() => {
    const setupCamera = async (): Promise<void> => {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await new Promise(resolve => {
          videoRef.current!.onloadedmetadata = () => resolve(true);
        });
      }
    };

    const loadModels = async (): Promise<void> => {

      const vision = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm"
      );

      // Resolve full runtime URLs for model assets so paths work both in
      // Vite dev and when the built frontend is served from a backend origin.
      const basePath = (typeof window !== 'undefined')
        ? `${window.location.origin}${import.meta.env.BASE_URL ?? '/'}`
        : '/';

      const faceModelPath = `${basePath}models/face_detector_short_range.tflite`;
      const gestureModelPath = `${basePath}models/gesture_recognizer.task`;
      console.log(faceModelPath)
      console.log(gestureModelPath)
      faceDetectorRef.current = await FaceDetector.createFromOptions(vision, {
        baseOptions: {
        modelAssetPath: faceModelPath
        },
        runningMode: 'VIDEO'
      });

      gestureRecognizerRef.current = await GestureRecognizer.createFromOptions(vision, {
        baseOptions: {
        modelAssetPath: gestureModelPath
        },
        runningMode: 'VIDEO'
      });
    };

    const detect = async (): Promise<void> => {
      const canvas = canvasRef.current;
      const ctx = canvas?.getContext('2d');
      const video = videoRef.current;
      if (!video || !canvas || !ctx || !faceDetectorRef.current || !gestureRecognizerRef.current) return;

      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      const now = performance.now();
      const shouldUpdate = now - lastUpdateTimeRef.current > 1000;

      //Run update every X seconds to preserve compute
      if (shouldUpdate) {
        // Face detection
        const faceResult = await faceDetectorRef.current.detectForVideo(video, now);
        const faceFound = faceResult.detections.length > 0;

        // Gesture detection
        const gestureResult = await gestureRecognizerRef.current.recognizeForVideo(video, now);
        const thumbsUp = gestureResult.gestures.some((gestureList: any[]) =>
          gestureList.some((gesture: { categoryName: string; score: number; }) => gesture.categoryName === 'Thumb_Up' && gesture.score > 0.66)
        );
        console.log(`Is giving thumbs up: ${thumbsUp} and face is shown: ${faceFound}`)
        setIsGivingConsent((faceFound && thumbsUp))
        lastUpdateTimeRef.current = now;
      }

      requestAnimationFrame(detect);
    };


    const init = async (): Promise<void> => {
      console.log("Local Face & Gesture Detection")
      await setupCamera();
      await loadModels();
      detect();
    };

    init();
  }, []);

  return (
    <div>
      <video ref={videoRef} autoPlay playsInline muted />
      <canvas style={{"visibility": "hidden", "display": "none"}} ref={canvasRef}/>
    </div>
  );
};

export default FaceAndGestureDetection;