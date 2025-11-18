/**
 * This component displays the live video feed from the user's camera.
 * It captures frames and sends them to the parent via onFrameCapture().
 */

import React, { useEffect, useRef, useState } from "react";

interface CameraFeedProps {
  onFrameCapture: (frame: Blob) => void;
  width?: number;
  height?: number;
  state: { [key: string]: any };
}

const CameraFeed: React.FC<CameraFeedProps> = ({
  onFrameCapture,
  width = 1280,
  height = 720,
  state,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [videoReady, setVideoReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const startCamera = async () => {
      console.log("📸 Requesting camera access...");

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            frameRate: { ideal: 30, max: 60 },
          },
          audio: false,
        });

        if (videoRef.current) {
          console.log("✅ Attaching video stream...");
          videoRef.current.srcObject = stream;

          videoRef.current.onloadedmetadata = () => {
            console.log("▶️ Playing video...");
            videoRef.current?.play();
            setVideoReady(true);
          };
        }
      } catch (err: any) {
        console.error("❌ Camera access error:", err);
        setError(err.message || "Unable to access camera");
      }
    };

    startCamera();

    return () => {
      // Stop camera when component unmounts
      if (videoRef.current?.srcObject) {
        const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
        tracks.forEach((track) => track.stop());
      }
    };
  }, []);

  useEffect(() => {
    if (!videoReady || !onFrameCapture) return;

    const captureFrame = () => {
      if (!videoRef.current || !canvasRef.current) return;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");
      ctx?.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

      canvas.toBlob((blob) => {
        if (blob) onFrameCapture(blob);
      }, "image/jpeg", 0.9);
    };

    const intervalTime = state?.Idle ? 500 : 66;
    const interval = setInterval(captureFrame, intervalTime);

    return () => clearInterval(interval);
  }, [videoReady, onFrameCapture, state]);

  return (
    <div className="video-feed">
      {error ? (
        <div style={{ color: "red", textAlign: "center" }}>
          <p>Camera Error: {error}</p>
          <p>Please check browser permissions and reload.</p>
        </div>
      ) : (
        <video
          ref={videoRef}
          autoPlay
          playsInline
          width={width}
          height={height}
          style={{ transform: "scaleX(-1)" }}
        />
      )}
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        style={{ display: "none" }}
      />
    </div>
  );
};

export default CameraFeed;
