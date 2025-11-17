import React, { useState, useRef, useEffect } from "react";
import "./styles/style.css";
import CameraFeed from "./components/CameraFeed";
import SocketHandler from "./components/SocketHandler";
import Instructions from "./components/Instructions";
import ServerFeed from "./components/ServerFeed";
import FilterFrames from "./components/FilterFrames";
import ProgressCircle from "./components/ProgressCircle";
import DownloadPrompt from "./components/DownloadPrompt";
import filtercolors from './assets/filtercolors.json'
import FaceAndGestureDetection from "./components/ConsentCamera";
import ConsentForm from "./components/ConsentForm";

const showConsent = import.meta.env.VITE_SHOW_CONSENT == "true";

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
  let qrTimeout: NodeJS.Timeout | undefined = undefined;
  const intervalRef = useRef<NodeJS.Timeout | null>(null); // Ref to store the interval ID
  const paintingTimerRef = useRef<number>(paintingTimer); // Ref to store the painting timer

  const [isGivingConsent, setIsGivingConsent] = useState<boolean>(false);

  // For testing purposes. Set to true when the core version is set to main (closed fist closes the artistic view)
  // Set to false when the core version is set to alternate (artistic view closes on a timer)
  const needsInstruction = true;

  // Map filter to highlight color
  const getHighlightColor = (filter: string) => {
    if (filter in filtercolors) {
      return filtercolors[filter as keyof typeof filtercolors];
    }
    else {
      return filtercolors["default"]
    }
  };

  const handleStateChange = (state: any) => {
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
    if (appState?.Idle === true) {
      console.log("Reset consent form")
      setIsGivingConsent(false)
    }
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
    //set frames ONLY if consent is given
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

  const defaultFeed = () => {
    return (
      <CameraFeed
        onFrameCapture={handleOutboundFrame}
        width={1280}
        height={720}
        state={appState}
      />
    )
  }


  const consentFeed = () => {
    if (isGivingConsent) {
      return (
        <CameraFeed
          onFrameCapture={handleOutboundFrame}
          width={1280}
          height={720}
          state={appState}
        />
      )
    } else {
      return (
        <div>
          <FaceAndGestureDetection setIsGivingConsent={setIsGivingConsent}></FaceAndGestureDetection>
          {(isGivingConsent == false) && <ConsentForm></ConsentForm>}      
        </div>
      )
    }
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
      <ServerFeed state={appState} artisticFrame={inboundFrame} visible={serverFeedVisible} filter={chosenFilter} paintingTimer={chosenFilterPerformance} needsInstruction={needsInstruction} />
    </div>

    <div
      className={`${serverFeedVisible ? "hidden" : "camera-feed-container"}`}>
      <ProgressCircle idle={appState.Idle ? true : false} position={handPosition} progress={progress} />


      {showConsent ? consentFeed() : defaultFeed() }

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
