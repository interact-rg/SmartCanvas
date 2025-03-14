/**
 * This element displays the video feed from the client side camera.
 */

import React, { useEffect, useRef, useState } from "react";
import { Socket } from "socket.io-client";

// Allow the video frame size to be customized
interface CameraFeedProps {
    //    onFrame: (video: HTMLVideoElement) => void;
    socket: Socket | null;
    width?: number;
    height?: number;
}

const CameraFeed: React.FC<CameraFeedProps> = ({ socket, width = 1280, height = 720 }: CameraFeedProps) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [videoReady, setVideoReady] = useState(false);

    useEffect(() => {
        const startCamera = async () => {
            console.log("Requesting camera access...");
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: { ideal: 1280 }, height: { ideal: 720 } },
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

    // useEffect(() => {
    //     const interval = setInterval(() => {
    //         if (videoRef.current) {
    //             console.log("Sending video frame to App.tsx"); 
    //             onFrame(videoRef.current);
    //         }
    //     }, 100);

    //     return () => clearInterval(interval);
    // }, [onFrame]);

    useEffect(() => {
        if (!socket) {
            console.log("Socket not connected yet...");
            return;
        }
    
        if (!videoReady) {
            console.log("Video not ready yet...");
            return;
        }
    
        console.log("Setting up video frame capture...");
        const FPS = 10;
        const interval = setInterval(() => {
            if (videoRef.current && canvasRef.current) {
                console.log("Sending video frame to backend...");
                const canvas = canvasRef.current;
                const context = canvas.getContext("2d");
                context?.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
                const imageDataUrl = canvas.toDataURL("image/jpeg");
                socket.emit("produce", imageDataUrl);
            }
        }, 1000 / FPS);
    
        return () => clearInterval(interval);
    }, [socket, videoReady]);


    return (
        <div className="video-feed" >
            <video ref={videoRef} autoPlay playsInline width={width} height={height} />
            <canvas ref={canvasRef} width={width} height={height} style={{ display: "none" }} />
        </div>
    );
};

export default CameraFeed;