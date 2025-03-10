import { useEffect, useRef, useState } from "react";
import { GestureRecognizer, FilesetResolver } from "@mediapipe/tasks-vision";

interface GestureRecognizerProps {
    video: HTMLVideoElement | null;
}

const GestureRecognizerComponent = ({ video }: GestureRecognizerProps) => {
    const [gesture, setGesture] = useState<string>("No Gesture");
    const gestureRecognizerRef = useRef<GestureRecognizer | null>(null);
    const isProcessingRef = useRef<boolean>(false); // Prevents multiple loops

    // Load the gesture recognition model
    useEffect(() => {
        const loadGestureRecognizer = async () => {
            try {
                const vision = await FilesetResolver.forVisionTasks(
                    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3/wasm"
                );

                gestureRecognizerRef.current = await GestureRecognizer.createFromOptions(vision, {
                    baseOptions: {
                        modelAssetPath: "/models/gesture_recognizer.task",
                        delegate: "GPU",
                    },
                    runningMode: "VIDEO",
                    numHands: 2,
                });

                console.log("Gesture Recognizer Loaded");
            } catch (error) {
                console.error("Error loading gesture recognizer:", error);
            }
        };

        loadGestureRecognizer();
    }, []); 

    // Process video frames continuously
    const processVideo = async () => {
        if (!gestureRecognizerRef.current || !video || !isProcessingRef.current) return;

        try {
            const results = await gestureRecognizerRef.current.recognizeForVideo(video, Date.now());

            if (results.gestures.length > 0) {
                setGesture(prevGesture => 
                    results.gestures[0][0].categoryName !== prevGesture 
                        ? results.gestures[0][0].categoryName 
                        : prevGesture
                );
            } else {
                setGesture("No Gesture");
            }
        } catch (error) {
            console.error("Gesture recognition error:", error);
        }

        requestAnimationFrame(() => processVideo());
    };

    // Start gesture recognition loop
    useEffect(() => {
        if (!video || !gestureRecognizerRef.current || isProcessingRef.current) return;

        isProcessingRef.current = true;
        processVideo();

        return () => {
            isProcessingRef.current = false;
        };
    }, [video, gestureRecognizerRef.current]); 

    return (
        <div style={{ textAlign: "center" }}>
            <h2>Gesture Recognition</h2>
            <p>Detected Gesture: <strong>{gesture}</strong></p>
        </div>
    );
};

export default GestureRecognizerComponent;
