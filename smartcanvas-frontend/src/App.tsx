import { useState } from "react";
import CameraFeed from "./components/CameraFeed";
import GestureRecognizerComponent from "./components/GestureRecognizerComponent";
import TopNav from "./components/TopNav";
import './styles/app.css'
import './styles/style.css'


const App = () => {
    const [videoElement, setVideoElement] = useState<HTMLVideoElement | null>(null);

    return (
        <div>
            <TopNav/>
       <div className="webcam-container">
            
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
        </div>
    );
};

export default App;
