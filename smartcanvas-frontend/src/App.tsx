import React, { useState, useRef, useEffect } from "react";
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
  const [qrCode, setQrCode] = useState<string | null>(""); // QR code sent by the server
  const [handPosition, setHandPosition] = useState<[number, number]>([0, 0]);
  const [progress, setProgress] = useState<number>(0);
  const [holdStill, setHoldStill] = useState<number>(0);
  const [paintingTimer, setPaintingTimer] = useState<number>(12); // Timer for the painting
  const [filters, setFilters] = useState<string[]>([]);
  const [chosenFilter, setChosenFilter] = useState<string>("");
  const [chosenFilterPerformance, setChosenFilterPerformance] = useState<number>(0);
  const [serverFeedVisible, setServerFeedVisible] = useState<boolean>(false);
  let qrTimeout: number | undefined = undefined;
  const intervalRef = useRef<number | null>(null); // Ref to store the interval ID
  const paintingTimerRef = useRef<number>(paintingTimer); // Ref to store the painting timer

  // Map filter to highlight color
  const getHighlightColor = (filter: string) => {
    switch (filter) {
      case "mosaic":
        return "lightskyblue";
      case "oil painting":
        return "orange";
      case "painterly":
        return "darkblue";
      case "pointillism":
        return "goldenrod";
      case "watercolor":
        return "lightsalmon";
      case "testfilter":
        return "green";
      default:
        return "#706EBD"; // Default purple
    }
  };

  const handleStateChange = (state: any) => {
    //console.log("State change received in App: ", state);
    if (state.Countdown) {
      clearTimeout(qrTimeout);
      setQrCode(null);
      setInboundFrame("");
    }
    if (state.ShowPic || state.Painting || state.Painting === false) {
      if (!serverFeedVisible) setServerFeedVisible(true);

      if (state.Painting) {
        setAppState(state);

        if (intervalRef.current) clearInterval(intervalRef.current);

        intervalRef.current = setInterval(() => {
          setPaintingTimer((prev) => {
            if (prev <= 1) {
              if (intervalRef.current) clearInterval(intervalRef.current);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      }
      else if (state.ShowPic && paintingTimerRef.current > 0) {
        console.log("Painting timer left: ", paintingTimerRef.current);
        setTimeout(() => {
          setAppState(state);
        }, paintingTimerRef.current * 1000);
      }
      else {
        setAppState(state);
      }
    } else {
      setServerFeedVisible(false);
      setAppState(state);
    }
  };

  useEffect(() => {
    //console.log("App state: ", appState);
  }, [appState]);

  useEffect(() => {
    // Set painting timer to the chosen filter performance
    if (chosenFilterPerformance > 0) {
      setPaintingTimer(Math.floor(chosenFilterPerformance) - 4); // Subtract 4 seconds for the countdown
      //console.log("Painting timer set to: ", Math.floor(chosenFilterPerformance) -4); 
    } else {
      setPaintingTimer(12);
      //console.log("Painting timer set to default 12 seconds");
    }
  }, [chosenFilterPerformance]);

  useEffect(() => {
    paintingTimerRef.current = paintingTimer;
    //console.log("Painting timer updated:", paintingTimer);
  }, [paintingTimer]);

  const handleOutboundFrame = (frame: Blob) => {
    setOutboundFrame(frame);
  };

  const handleQrCode = (qr: string) => {
    setQrCode(qr);
    clearTimeout(qrTimeout);
    qrTimeout = setTimeout(() => {
      setQrCode(null);
      setInboundFrame("");
    }, 60000);
  };

  const handleHoldStill = (timer: number) => {
    setHoldStill(timer);
    //console.log("Painting timer: ", timer);
  };

  const handleArtisticFrame = (frame: string) => {
    setInboundFrame(frame);
  }

  return (
    <div id="mainContainer" className="container_fs" style={{ "--color-highlight": getHighlightColor(chosenFilter) } as React.CSSProperties}>
      <SocketHandler
        onStateChange={handleStateChange}
        videoFrame={outboundFrame}
        onArtisticFrame={handleArtisticFrame}
        onHandPosition={setHandPosition}
        onProgress={setProgress}
        onHoldStill={handleHoldStill}
        onFilters={setFilters}
        onChosenFilter={setChosenFilter}
        onFilterPerformance={setChosenFilterPerformance}
        onQrCode={handleQrCode}
      />

      <div
        className={`${serverFeedVisible ? "server-feed-container" : "hidden"}`}>
        <ServerFeed state={appState} artisticFrame={inboundFrame} visible={serverFeedVisible} filter={chosenFilter} paintingTimer={chosenFilterPerformance}/>
      </div>

      <div
        className={`${serverFeedVisible ? "hidden" : "camera-feed-container"}`}>
        <ProgressCircle idle={appState.Idle ? true : false} position={handPosition} progress={progress} />
        <CameraFeed
          onFrameCapture={handleOutboundFrame}
          width={1280}
          height={720}
          state={appState}
        />
        <Instructions state={appState} countdown={holdStill} filter={chosenFilter} />
        <FilterFrames availableFilters={filters} chosenFilter={chosenFilter} />
      </div>

      {!(appState.Painting == true || appState.Painting == false) && <DownloadPrompt
        image={inboundFrame}
        downloadQr={qrCode}
      />}
    </div>
  );
};

export default App;
