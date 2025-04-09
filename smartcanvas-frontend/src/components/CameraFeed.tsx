/**
 * This element displays the video feed from the client side camera.
 */

import React, { useEffect, useRef, useState } from "react";

// Allow the video frame size to be customized
interface CameraFeedProps {
    onFrameCapture: (frame: Blob) => void;
    width?: number;
    height?: number;
    state: { [key: string]: any };
}

const CameraFeed: React.FC<CameraFeedProps> = ({ onFrameCapture, width = 1280, height = 720, state }: CameraFeedProps) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [videoReady, setVideoReady] = useState(false);

    useEffect(() => {
        const startCamera = async () => {
            console.log("Requesting camera access...");
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: { ideal: 1280 }, height: { ideal: 720 }, frameRate: { ideal: 30, max: 60 } },
                audio: false,
            });

            if (videoRef.current) {
                console.log("Attaching video stream...");
                videoRef.current.srcObject = stream;

                videoRef.current.onloadedmetadata = () => {
                    console.log("Playing video...");
                    videoRef.current?.play();
                    setVideoReady(true);                    
                };
                
            }
        }
        startCamera();

    }, []);

    useEffect(() => {
        if (!videoReady || onFrameCapture === undefined) {
            //console.log("Video not ready yet...");
            return;
        }
        
        const captureFrame = () => {
            if (videoRef.current && canvasRef.current) {
                //console.log("Capturing frame...");
                const canvas = canvasRef.current;
                const context = canvas.getContext("2d");
                context?.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
                
                // Convert to Blob and send it to parent component
                canvas.toBlob((blob) => {
                    if (blob) onFrameCapture(blob);
                }, "image/jpeg", 1.0);
            }

        };

        // Adjust the interval based on the app state
        const intervalTime = state.Idle ? 500 : 33; // 500ms for Idle state, 33ms for other states

        const interval = setInterval(() => {
            if (videoReady) {
                //console.log("Interval time is: ", intervalTime);
                captureFrame();
            } 
        }, intervalTime); // Tries every intervalTime ms but only if the video is ready


        return () => {
            clearInterval(interval);
        };
    }, [videoReady, onFrameCapture, state]);

    return (
        <div className="video-feed" >
            <video ref={videoRef} autoPlay playsInline width={width} height={height} style={{ transform: 'scaleX(-1)' }} />
            <canvas ref={canvasRef} width={width} height={height} style={{ display: "none" }} />
        </div>
    );
};

export default CameraFeed;