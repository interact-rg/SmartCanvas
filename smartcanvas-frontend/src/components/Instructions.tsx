/**
 * Component to show different instructions based on the state of the application
 */
import React, { useState, useEffect } from "react";
import waving_hand from "../assets/five_fingers.png";
import "../styles/hand.css";
import swiping_hand from "../assets/swiping_hand.png";

interface InstructionsProps {
  state: { [key: string]: any };
  countdown: number;
  filter: string;
}

const Instructions: React.FC<InstructionsProps> = ({
  state,
  countdown = 4,
  filter,
}) => {
  const [randomColumn, setRandomColumn] = useState<number>(1); // Random column (1, 2, or 3)
  const [waveIsVisible, setWaveIsVisible] = useState<boolean>(true); // Toggle visibility of the waving hand
  const [swipeIsVisible, setSwipeVisible] = useState<boolean>(true); //instructions (swiping_hand) should be invisible for n seconds after filter is changed (user has learned how to switch filters, so instructions don't need to be visible)
  const [swipeUsed, setSwipeUsed] = useState<boolean>(false); // Flag to track if swiping hand has been used
  const [holdHandVisible, setHoldHandVisible] = useState<boolean>(false); // Flag to track if hold hand still instruction is visible
  // Function to generate a random column ID (1, 2, or 3)
  const getRandomColumn = () => Math.floor(Math.random() * 3) + 1;

  useEffect(() => {
    // Timer to toggle visibility and randomize column every N seconds
    const interval = setInterval(() => {
      setWaveIsVisible((prev) => !prev); // Toggle visibility
      if (!waveIsVisible) {
        setRandomColumn(getRandomColumn()); // Randomize column when becoming visible
      }
    }, 5000);

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, [waveIsVisible]);

  useEffect(() => {
    if (state.Countdown) {
      countdown = 4; // Reset countdown to 4 seconds when countdown state is active
    }
    if (state.Idle) {
      setSwipeVisible(true); // Reset swiping hand visibility when Idle state is active
      setSwipeUsed(false); // Reset the flag when Idle state is active
    } else if (state.Active && !swipeUsed) {
      // Show swiping hand every 4.5 seconds only if it hasn't been used yet
      const interval = setInterval(() => {
        setSwipeVisible((prev) => !prev); // Toggle visibility
      }, 4500);

      return () => clearInterval(interval); // Cleanup interval on unmount
    }
  }, [state, swipeUsed]);

  useEffect(() => {
    // Timer to toggle visibility of hold hand symbol every 6 seconds
    const interval = setInterval(() => {
      setHoldHandVisible((prev) => !prev); // Toggle visibility
    }, 6000);

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, [holdHandVisible]);

  useEffect(() => {
    if (state.Active) {
      // Hide swiping hand after the filter is changed
      setSwipeVisible(false);
      setSwipeUsed(true); // Set the flag to indicate that swiping hand has been used
    }
  }, [filter]);

  const renderInstructions = () => {
    for (const [key, value] of Object.entries(state)) {
      if (value) {
        switch (key) {
          case "Startup":
            return (
              <div className="full-container">
                <h1>SmartCanvas</h1>
              </div>
            );
          case "Idle":
            return (
              <div className="top-row">
                <div className="column" id="column-1">
                  {waveIsVisible && randomColumn === 1 && (
                    <img
                      src={waving_hand}
                      id="hand"
                      style={{ maxWidth: "20%", marginLeft: "30%" }}
                    />
                  )}
                </div>
                <div className="column" id="column-2">
                  {waveIsVisible && randomColumn === 2 && (
                    <img
                      src={waving_hand}
                      id="hand"
                      style={{ maxWidth: "20%", marginLeft: "30%" }}
                    />
                  )}
                </div>
                <div className="column" id="column-3">
                  {waveIsVisible && randomColumn === 3 && (
                    <img
                      src={waving_hand}
                      id="hand"
                      style={{ maxWidth: "20%", marginLeft: "30%" }}
                    />
                  )}
                </div>
              </div>
            );
          case "Active":
            return (
              <div className="instructions">
                <button onClick={renderGDPR} style={{maxHeight: '10%', maxWidth: '10%'}}> GDPR test button </button>
                <div className="top-row">
                  <div className="column" id="column-1"></div>
                  <div className="column" id="column-2">
                    {swipeIsVisible && (
                      <img
                        src={swiping_hand}
                        id="two_fingers_icon"
                        style={{ maxWidth: "20%" }}
                      />
                    )}
                  </div>
                  <div className="column" id="column-3">
                    {holdHandVisible && (
                      <img
                        src={waving_hand}
                        id="hand_still"
                        style={{ maxWidth: "20%", marginLeft: "30%" }}
                      />
                    )}
                  </div>
                </div>
                <div className="bottom-row"></div>
              </div>
            );
          case "Countdown":
            return (
              <div className="full-container">
                <div className="big-text">{renderCountdown()}</div>
              </div>
            );

          default:
            return <></>;
        }
      }
    }
    return <></>;
  };

  const renderGDPR = () => {
    return (
      <div> YEET </div>
    );
  }

  const renderCountdown = () => {
    if (countdown > 0) {
      // Round the countdown down to the nearest integer
      return Math.floor(countdown);
    }
  };

  // const hideSwipingHand = () => {
  //   setSwipeVisible((prev) => !prev);
  //   console.log("swiping_hand set invisible (should be false): " + swipeIsVisible)
  //   setTimeout( function () {
  //     console.log("swiping_hand set invisible (should be false): " + swipeIsVisible)
  //     setSwipeVisible((prev) => !prev);
  //     console.log("Swiping hand visible (should be true): " + swipeIsVisible)
  //   }, 5000);

  // }

  return <div className="instructions">{renderInstructions()}</div>;
};

export default Instructions;
