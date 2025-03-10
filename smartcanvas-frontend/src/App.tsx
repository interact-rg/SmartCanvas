import { useState } from "react";
import CameraFeed from "./components/CameraFeed";
import GestureRecognizerComponent from "./components/GestureRecognizerComponent";
import './app.css'


const App = () => {
    const [videoElement, setVideoElement] = useState<HTMLVideoElement | null>(null);

    return (
        <div>
            <h1>Smartest Canvas</h1>
            <img src="https://interact.oulu.fi/site/files/make4change/interact-logo.png" className="logo" />

            {/* Camera component captures video frames */}
            <CameraFeed onFrame={(video) => {
                setVideoElement(video);
            }} />

            {/* Gesture recognizer processes video frames */}
            {videoElement ? (
                <GestureRecognizerComponent video={videoElement} />
            ) : (
                <p>Waiting for video...</p>
            )}
        </div>
    );
};

export default App;
