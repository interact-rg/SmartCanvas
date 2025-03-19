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
    const [canSendFrame, setCanSendFrame] = useState(true);

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

        const sendFrame = () => {
            if (!canSendFrame) return; // Wait for ack before sending a new frame

            if (videoRef.current && canvasRef.current) {
                console.log("Sending video frame to backend...");
                const canvas = canvasRef.current;
                const context = canvas.getContext("2d");
                context?.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
                const imageDataUrl = canvas.toDataURL("image/jpeg");

                socket.emit("produce", imageDataUrl);
                //setCanSendFrame(false); // Prevent sending until ack is received
            }
        };

        // Listen for acknowledgment before sending the next frame
        const handleAck = () => {
            console.log("Ack received! Ready to send next frame.");
            setCanSendFrame(true);
        };

        socket.on("ack", handleAck);

        const interval = setInterval(() => {
            if (canSendFrame) {
                sendFrame();
            } 
        }, 100); // Tries every 100ms but only sends if allowed

        return () => {
            clearInterval(interval);
            socket.off("ack", handleAck);
        };
    }, [socket, videoReady, canSendFrame])


    return (
        <div className="video-feed" >
            <video ref={videoRef} autoPlay playsInline width={width} height={height} />
            <canvas ref={canvasRef} width={width} height={height} style={{ display: "none" }} />
        </div>
    );
};

export default CameraFeed;