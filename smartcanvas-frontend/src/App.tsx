import React, { useState } from "react";
import "./styles/style.css";
import CameraFeed from "./components/CameraFeed";
import SocketHandler from "./components/SocketHandler";
import Instructions from "./components/Instructions";
import ServerFeed from "./components/ServerFeed";
import FilterFrames from "./components/FilterFrames";
import ProgressCircle from "./components/ProgressCircle";
import DownloadPrompt from "./components/DownloadPrompt";

const App: React.FC = () => {
  const [appState, setAppState] = useState<any>({});
  const [outboundFrame, setOutboundFrame] = useState<Blob | null>(null); // Frame that is sent to the server
  const [inboundFrame, setInboundFrame] = useState<string>(""); // Artistic picture sent by the server
  const [qrCode, setQrCode] = useState<string|null>(""); // QR code sent by the server
  const [handPosition, setHandPosition] = useState<[number, number]>([0, 0]);
  const [progress, setProgress] = useState<number>(0);
  const [painting, setPainting] = useState<number>(0);
  const [filters, setFilters] = useState<string[]>([]);
  const [chosenFilter, setChosenFilter] = useState<string>("");
  let qrTimeout: number|undefined = undefined;

  const handleStateChange = (state: any) => {
    //console.log("State change received in App: ", state);
    if (state.Countdown) {
      clearTimeout(qrTimeout);
      setQrCode(null);
    }
    setAppState(state);
  };

  const handleOutboundFrame = (frame: Blob) => {
    setOutboundFrame(frame);
  };

  const handleQrCode = (qr: string) => {
    setQrCode(qr);
    clearTimeout(qrTimeout);
    qrTimeout = setTimeout(() => {
      setQrCode(null);
    }, 60000);
  };

  const handlePainting = (timer: number) => {
    setPainting(timer);
    //console.log("Painting timer: ", timer);
  };

  return (
    <div id="mainContainer" className="container_fs">
      <SocketHandler
        onStateChange={handleStateChange}
        videoFrame={outboundFrame}
        onArtisticFrame={setInboundFrame}
        onHandPosition={setHandPosition}
        onProgress={setProgress}
        onPainting={handlePainting}
        onFilters={setFilters}
        onChosenFilter={setChosenFilter}
        onQrCode={handleQrCode}
      />

      <div
        className={`${appState.ShowPic ? "server-feed-container" : "hidden"}`}>
        <ServerFeed artisticFrame={inboundFrame} />
      </div>

      <div
        className={`${appState.ShowPic ? "hidden" : "camera-feed-container"}`}>
        <ProgressCircle position={handPosition} progress={progress} />
        <CameraFeed
          onFrameCapture={handleOutboundFrame}
          width={1280}
          height={720}
          state={appState}
        />
        <Instructions state={appState} countdown={painting} />
        <FilterFrames availableFilters={filters} chosenFilter={chosenFilter}/>
      </div>

      <DownloadPrompt
        image={inboundFrame}
        downloadQr={qrCode}
      />
    </div>
  );
};

export default App;
