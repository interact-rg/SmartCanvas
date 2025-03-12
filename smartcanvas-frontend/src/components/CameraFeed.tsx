import { useEffect, useRef, useState } from "react";

interface CameraFeedProps {
    onFrame: (video: HTMLVideoElement) => void;
}

const CameraFeed = ({ onFrame }: CameraFeedProps) => {
    const videoRef = useRef<HTMLVideoElement>(null);

    useEffect(() => {
        const startCamera = async () => {
                console.log("Requesting camera access...");
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });

                if (videoRef.current) {
                    console.log("Attaching video stream...");
                    videoRef.current.srcObject = stream;

                    videoRef.current.onloadedmetadata = () => {
                        console.log("Playing video...");
                        videoRef.current?.play();
                    };
                }
        }
        startCamera();
    }, []);

    useEffect(() => {
        const interval = setInterval(() => {
            if (videoRef.current) {
                console.log("Sending video frame to App.tsx"); 
                onFrame(videoRef.current);
            }
        }, 100);

        return () => clearInterval(interval);
    }, [onFrame]);

    return (
        <div style={{ textAlign: "center" }}>
            <video ref={videoRef} autoPlay playsInline width="640" height="480" />
        </div>
    );
};

export default CameraFeed;