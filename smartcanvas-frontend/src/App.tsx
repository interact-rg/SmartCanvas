import React, { useState } from "react";
import "./styles/style.css";
import CameraFeed from "./components/CameraFeed";
import SocketHandler from "./components/SocketHandler";
//import useSocket from "./hooks/useSocket";
import Instructions from "./components/Instructions";
import ServerFeed from "./components/ServerFeed";
import FilterFrames from "./components/FilterFrames";

const App: React.FC = () => {
  const [appState, setAppState] = useState<any>({});
  const [outboundFrame, setOutboundFrame] = useState<Blob | null>(null); // Frame that is sent to the server
  const [inboundFrame, setInboundFrame] = useState<string>(""); // Artistic picture sent by the server

  const handleStateChange = (state: any) => {
    console.log("State change received in App: ", state);
    setAppState(state);
  };

  const handleOutboundFrame = (frame: Blob) => {
    setOutboundFrame(frame);
  };

  const handleInboundFrame = (frame: string) => {
    setInboundFrame(frame);
  };

  return (
    <div id="mainContainer" className="container_fs">
      <SocketHandler
        onStateChange={handleStateChange}
        videoFrame={outboundFrame}
        onArtisticFrame={handleInboundFrame}
      />
      {/* <div className="header">
                <h1>Smart Canvas</h1>
                <img src="https://interact.oulu.fi/site/files/make4change/interact-logo.png" className="logo" />
            </div> */}

      <div
        className={`${appState.ShowPic ? "server-feed-container" : "hidden"}`}
      >
        <ServerFeed artisticFrame={inboundFrame} />
      </div>

      <div
        className={`${appState.ShowPic ? "hidden" : "camera-feed-container"}`}
      >
        <CameraFeed
          onFrameCapture={handleOutboundFrame}
          width={1280}
          height={720}
        />
        <Instructions state={appState} />
        <FilterFrames />
      </div>
    </div>
  );
};

export default App;
