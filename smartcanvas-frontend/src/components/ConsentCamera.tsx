import React, { useEffect, useRef } from "react";
import { Hands, Results } from "@mediapipe/hands";
import { Camera } from "@mediapipe/camera_utils";

interface ConsentCameraProps {
  onConsent: (accepted: boolean) => void;
  width?: number;
  height?: number;
}

const ConsentCamera: React.FC<ConsentCameraProps> = ({ onConsent, width = 640, height = 360 }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const cameraRef = useRef<Camera | null>(null);

  // Stable gesture detection
  const thumbsUpCount = useRef(0);
  const thumbsDownCount = useRef(0);
  const gestureThreshold = 5; // number of consecutive frames to confirm
  const consentGivenRef = useRef(false); // prevent multiple triggers

  useEffect(() => {
    if (!videoRef.current) return;

    const hands = new Hands({
      locateFile: (file) =>
        `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}` // load models from CDN
    });

    hands.setOptions({
      maxNumHands: 1,
      minDetectionConfidence: 0.7,
      minTrackingConfidence: 0.7,
    });

    hands.onResults((results: Results) => {
      if (consentGivenRef.current) return;

      if (!results.multiHandLandmarks || results.multiHandLandmarks.length === 0) {
        thumbsUpCount.current = 0;
        thumbsDownCount.current = 0;
        return;
      }

      const landmarks = results.multiHandLandmarks[0];
      const thumbTip = landmarks[4];
      const wrist = landmarks[0];

      const vertical = thumbTip.y - wrist.y;

      if (vertical < -0.25) {
        thumbsUpCount.current += 1;
        thumbsDownCount.current = 0;
        if (thumbsUpCount.current >= gestureThreshold) {
          consentGivenRef.current = true;
          onConsent(true);
        }
      } else if (vertical > 0.25) {
        thumbsDownCount.current += 1;
        thumbsUpCount.current = 0;
        if (thumbsDownCount.current >= gestureThreshold) {
          consentGivenRef.current = true;
          onConsent(false);
        }
      } else {
        thumbsUpCount.current = 0;
        thumbsDownCount.current = 0;
      }
    });

    cameraRef.current = new Camera(videoRef.current, {
      onFrame: async () => {
        await hands.send({ image: videoRef.current! });
      },
      width,
      height,
    });

    cameraRef.current.start();

    return () => {
      cameraRef.current?.stop();
    };
  }, [onConsent, width, height]);

  return (
    <div className="consent-camera" style={{ position: "relative" }}>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        width={width}
        height={height}
        style={{ transform: "scaleX(-1)" }}
      />
      {/* Optional: visual feedback */}
      <div
        style={{
          position: "absolute",
          bottom: 10,
          left: 10,
          width: `${(thumbsUpCount.current / gestureThreshold) * 100}%`,
          height: "5px",
          backgroundColor: "green",
          transition: "width 0.1s",
        }}
      />
    </div>
  );
};

export default ConsentCamera;
