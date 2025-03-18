import React, { useState } from "react";
import './styles/style.css'
import CameraFeed from "./components/CameraFeed";
import SocketHandler from "./components/SocketHandler";
import useSocket from "./hooks/useSocket";
import Instructions from "./components/Instructions";
import ServerFeed from "./components/ServerFeed";


const App: React.FC = () => {
    //const [videoElement, setVideoElement] = useState<HTMLVideoElement | null>(null);
    const socket = useSocket('http://localhost:5000');
    const [appState, setAppState] = useState<any>({});

    const handleStateChange = (state: any) => {
        console.log("State change received in App: ", state);
        setAppState(state);
    };

    return (
        <div id="mainContainer" className="container_fs">
            <SocketHandler socket={socket} onStateChange={handleStateChange} />
            <div className="header">
                <h1>Smartest Canvas</h1>
                <img src="https://interact.oulu.fi/site/files/make4change/interact-logo.png" className="logo" />
            </div>
            {appState.ShowPic ? (
                <div className="server-feed-container">
                    <ServerFeed socket={socket} />
                </div>
            ) : (
                <div className="camera-feed-container">
                    <CameraFeed socket={socket} width={1280} height={720} />
                    <Instructions state={appState} />
                </div>
            )}
        </div>
    );
};

export default App;
