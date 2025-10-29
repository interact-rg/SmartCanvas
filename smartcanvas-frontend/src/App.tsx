import React, { useState, useRef, useEffect } from "react";
import "./styles/style.css";
import CameraFeed from "./components/CameraFeed";
import SocketHandler from "./components/SocketHandler";
import Instructions from "./components/Instructions";
import ServerFeed from "./components/ServerFeed";
import FilterFrames from "./components/FilterFrames";
import ProgressCircle from "./components/ProgressCircle";
import DownloadPrompt from "./components/DownloadPrompt";
import filtercolors from './assets/filtercolors.json';

const App: React.FC = () => {
  const [appState, setAppState] = useState<any>({});
  const [outboundFrame, setOutboundFrame] = useState<Blob | null>(null);
  const [inboundFrame, setInboundFrame] = useState<string>("");
  const [qrCode, setQrCode] = useState<string | null>("");
  const [handPosition, setHandPosition] = useState<[number, number]>([0, 0]);
  const [progress, setProgress] = useState<number>(0);
  const [holdStill, setHoldStill] = useState<number>(0);
  const [paintingTimer, setPaintingTimer] = useState<number>(12);
  const [filters, setFilters] = useState<string[]>([]);
  const [chosenFilter, setChosenFilter] = useState<string>("");
  const [chosenFilterPerformance, setChosenFilterPerformance] = useState<number>(0);
  const [serverFeedVisible, setServerFeedVisible] = useState<boolean>(false);

  const intervalRef = useRef<number | null>(null);
  const paintingTimerRef = useRef<number>(paintingTimer);
  const needsInstruction = true;

  // ⚡ Force popup on first load
  const [showConsentPopup, setShowConsentPopup] = useState<boolean>(true);

  let qrTimeout: number | undefined = undefined;

  const getHighlightColor = (filter: string) => {
    if (filter in filtercolors) return filtercolors[filter as keyof typeof filtercolors];
    return filtercolors["default"];
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
      } else if (state.ShowPic && paintingTimerRef.current > 0) {
        setTimeout(() => setAppState(state), paintingTimerRef.current * 1000);
      } else {
        setAppState(state);
      }
    } else {
      setServerFeedVisible(false);
      setAppState(state);
    }
  };

  useEffect(() => {
    paintingTimerRef.current = paintingTimer;
  }, [paintingTimer]);

  useEffect(() => {
    if (chosenFilterPerformance > 0) {
      setPaintingTimer(Math.floor(chosenFilterPerformance) - 4);
    } else {
      setPaintingTimer(12);
    }
  }, [chosenFilterPerformance]);

  const handleOutboundFrame = (frame: Blob) => setOutboundFrame(frame);
  const handleQrCode = (qr: string) => {
    setQrCode(qr);
    clearTimeout(qrTimeout);
    qrTimeout = setTimeout(() => {
      setQrCode(null);
      setInboundFrame("");
    }, 60000);
  };
  const handleHoldStill = (timer: number) => setHoldStill(timer);
  const handleArtisticFrame = (frame: string) => setInboundFrame(frame);

  // Optional: gesture-based consent
  const handleGestureConsent = (gesture: string) => {
    if (!showConsentPopup) return;
    if (gesture === "thumbs_up") {
      localStorage.setItem("gdpr_consent", "accepted");
      setShowConsentPopup(false);
    } else if (gesture === "thumbs_down") {
      localStorage.setItem("gdpr_consent", "declined");
      setShowConsentPopup(false);
    }
  };

  return (
    <div
      id="mainContainer"
      className="container_fs"
      style={{ "--color-highlight": getHighlightColor(chosenFilter) } as React.CSSProperties}
    >
      {/* ⚡ Consent Popup */}
      {showConsentPopup && (
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
          }}
        >
          <h2>Consent for Image Processing</h2>
          <p>
            University of Oulu requires your consent to process your camera feed for generating cartoon images.
            Give a 👍 to accept or 👎 to decline.
          </p>
          <button
            style={{ fontSize: "2rem", margin: "10px" }}
            onClick={() => {
              localStorage.setItem("gdpr_consent", "accepted");
              setShowConsentPopup(false);
            }}
          >
            👍 Accept
          </button>
          <button
            style={{ fontSize: "2rem", margin: "10px" }}
            onClick={() => {
              localStorage.setItem("gdpr_consent", "declined");
              setShowConsentPopup(false);
            }}
          >
            👎 Decline
          </button>
        </div>
      )}

      {/* ⚡ Only render app after consent */}
      {!showConsentPopup && (
        <>
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
            onGesture={handleGestureConsent}
          />

          <div className={`${serverFeedVisible ? "server-feed-container" : "hidden"}`}>
            <ServerFeed
              state={appState}
              artisticFrame={inboundFrame}
              visible={serverFeedVisible}
              filter={chosenFilter}
              paintingTimer={chosenFilterPerformance}
              needsInstruction={needsInstruction}
            />
          </div>

          <div className={`${serverFeedVisible ? "hidden" : "camera-feed-container"}`}>
            <CameraFeed
              onFrameCapture={handleOutboundFrame}
              width={1280}
              height={720}
              state={appState}
            />
            <ProgressCircle idle={appState.Idle ? true : false} position={handPosition} progress={progress} />
            <Instructions state={appState} countdown={holdStill} filter={chosenFilter} />
            <FilterFrames availableFilters={filters} chosenFilter={chosenFilter} />
          </div>

          {!(appState.Painting === true || appState.Painting === false) && (
            <DownloadPrompt image={inboundFrame} downloadQr={qrCode} />
          )}
        </>
      )}
    </div>
  );
};

export default App;
