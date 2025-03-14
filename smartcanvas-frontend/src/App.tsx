import React, { useState } from "react";
import './styles/style.css'
import CameraFeed from "./components/CameraFeed";
// import TopNav from "./components/TopNav";
import SocketHandler from "./components/SocketHandler";
import useSocket from "./hooks/useSocket";


const App: React.FC = () => {
    //const [videoElement, setVideoElement] = useState<HTMLVideoElement | null>(null);
    const socket = useSocket('http://localhost:5000');

    return (
        <div id="mainContainer" className="container_fs">
            <SocketHandler socket={socket}/>
            <div className="webcam-container">

                <h1>Smartest Canvas</h1>
                <img src="https://interact.oulu.fi/site/files/make4change/interact-logo.png" className="logo" />

                {/* Camera component captures video frames */}
                {/* <CameraFeed socket={socket} width={1024} height={768} onFrame={(video) => {
                    setVideoElement(video);
                }} /> */}
                <CameraFeed socket={socket} width={1024} height={768} />

            </div>
        </div>
    );
};

export default App;
