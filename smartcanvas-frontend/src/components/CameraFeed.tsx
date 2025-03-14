import { useEffect, useRef, useState } from "react";

// Allow the video frame size to be customized
interface CameraFeedProps {
    onFrame: (video: HTMLVideoElement) => void;
    width?: number;
    height?: number;
}

const CameraFeed = ({ onFrame, width = 640, height = 480 }: CameraFeedProps) => {
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
        <div className="video-feed" >
            <video ref={videoRef} autoPlay playsInline width={width} height={height} />
        </div>
    );
};

export default CameraFeed;