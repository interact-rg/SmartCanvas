import { useEffect, useRef, useState } from "react";

interface CameraFeedProps {
    onFrame: (video: HTMLVideoElement) => void;
}

const CameraFeed = ({ onFrame }: CameraFeedProps) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [error, setError] = useState<string | null>(null); // Store error messages

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

        return () => {
            if (videoRef.current?.srcObject) {
                console.log("Stopping camera stream...");
                const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
                tracks.forEach((track) => track.stop());
            }
        };
    }, []);

    useEffect(() => {
        const interval = setInterval(() => {
            if (videoRef.current) {
                console.log("Sending video frame to App.tsx"); // ✅ Debugging
                onFrame(videoRef.current);
            }
        }, 100);

        return () => clearInterval(interval);
    }, [onFrame]);

    return (
        <div style={{ textAlign: "center" }}>
            <h2>Camera Feed</h2>
            {error && <p style={{ color: "red" }}>{error}</p>}
            <video ref={videoRef} autoPlay playsInline width="640" height="480" />
        </div>
    );
};

export default CameraFeed;