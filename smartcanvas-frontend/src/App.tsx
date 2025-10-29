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
    if(appState?.Idle === true){
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

  const consentForm = () => {
      return (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(0,0,0,0.85)",
            color: "white",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 99999,
            textAlign: "center",
            padding: "20px",
            pointerEvents: "auto",
            fontSize: "1.5rem",
            boxSizing: "border-box",     // include padding in width
            overflowX: "hidden"          // extra safety to prevent horizontal scroll
          }}
        >
          <h2>Consent for Image Processing</h2>
          <p>
  University of Oulu requires your consent to process your camera feed for AI-generated images. 
  Your consent will be given using gestures: <strong>👍 for "I agree"</strong> or <strong>👎 for "I do not agree"</strong>.
</p>
<ul>
  <li>👍 Gesture: You agree to the processing of your camera feed for generating AI-based images.</li>
  <li>👎 Gesture: You do not agree to the processing of your camera feed.</li>
  <li>Your image will <strong>not be permanently stored</strong> and will only be held for a few seconds during processing.</li>
  <li>The AI-generated image is created temporarily and is used only within the application.</li>
  <li>No personal data beyond the camera feed will be collected or saved.</li>
</ul>
<p>
  By giving consent via gestures, you acknowledge that the processing is performed for AI-generated image purposes only and all data is handled securely and temporarily.
</p>

          <button
            style={{ fontSize: "2rem", margin: "10px" }}
            onClick={() => {
              // localStorage.setItem("gdpr_consent", "accepted");
              // setShowConsentPopup(false);
              // setHasConsent(true)
            }}
          >
            👍 Accept
          </button>
          <button
            style={{ fontSize: "2rem", margin: "10px" }}
            onClick={() => {
              // localStorage.setItem("gdpr_consent", "declined");
              // setShowConsentPopup(false);
              // setHasConsent(false)
            }}
          >
            👎 Decline
          </button>
        </div>
      )
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
        <ServerFeed state={appState} artisticFrame={inboundFrame} visible={serverFeedVisible} filter={chosenFilter} paintingTimer={chosenFilterPerformance} needsInstruction={needsInstruction}/>
      </div>

      <div
        className={`${serverFeedVisible ? "hidden" : "camera-feed-container"}`}>
        <ProgressCircle idle={appState.Idle ? true : false} position={handPosition} progress={progress} />
        { isGivingConsent ?    
          <CameraFeed
            onFrameCapture={handleOutboundFrame}
            width={1280}
            height={720}
            state={appState}
          /> :
          <FaceAndGestureDetection setIsGivingConsent={setIsGivingConsent}></FaceAndGestureDetection>
        }

        <Instructions state={appState} countdown={holdStill} filter={chosenFilter} />
        <FilterFrames availableFilters={filters} chosenFilter={chosenFilter} />
      </div>

      {!(appState.Painting == true || appState.Painting == false) && <DownloadPrompt
        image={inboundFrame}
        downloadQr={qrCode}
      />}
      {(isGivingConsent == false) && consentForm()}
    </div>
  );
};

export default App;
