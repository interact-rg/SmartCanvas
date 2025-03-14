import { useState } from "react";
import CameraFeed from "./components/CameraFeed";
// import TopNav from "./components/TopNav";
import './styles/style.css'


const App = () => {
    const [videoElement, setVideoElement] = useState<HTMLVideoElement | null>(null);

    return (
        <div id="mainContainer" className="container_fs">

            <div className="webcam-container">

                <h1>Smartest Canvas</h1>
                <img src="https://interact.oulu.fi/site/files/make4change/interact-logo.png" className="logo" />

                {/* Camera component captures video frames */}
                <CameraFeed width={1024} height={768} onFrame={(video) => {
                    setVideoElement(video);
                }} />

            </div>
        </div>
    );
};

export default App;
