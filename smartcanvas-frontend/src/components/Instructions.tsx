/**
 * Component to show different instructions based on the state of the application
 */
import React, { useState, useEffect } from "react";
import waving_hand from "../assets/five_fingers.png";
import "../styles/hand.css";
import pointing_hand from "../assets/swiping_hand.png";

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
  const [pointingIsVisible, setPointingVisible] = useState<boolean>(true); // instructions (pointing_hand) should be invisible for n seconds after filter is changed (user has learned how to switch filters, so instructions don't need to be visible)
  const [pointingUsed, setPointingUsed] = useState<boolean>(false); // Flag to track if pointing hand has been used
  const [holdHandVisible, setHoldHandVisible] = useState<boolean>(false); // Flag to track if hold hand still instruction is visible
  const [showLeftHand, setShowLeftHand] = useState<boolean>(true); // Track which hand to show
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
      setPointingVisible(true); // Reset pointing hand visibility when Idle state is active
      setPointingUsed(false); // Reset the flag when Idle state is active
    } else if (state.Active && !pointingUsed) {
      // Show pointing hands every 6 seconds only if it hasn't been used yet
      const interval = setInterval(() => {
        setPointingVisible((prev) => !prev); // Toggle visibility
      }, 6000);

      return () => clearInterval(interval); // Cleanup interval on unmount
    }
  }, [state, pointingUsed]);

  useEffect(() => {
    // Function to toggle "hold hand" visibility
    const toggleVisibility = () => {
      setHoldHandVisible(true);
      setTimeout(() => {
        setHoldHandVisible(false); // Hide the hold hand after 5 seconds
      }, 5000);
    };

    // Start the interval to toggle visibility every 15 seconds (5 seconds visible + 10 seconds hidden)
    const interval = setInterval(toggleVisibility, 15000);

    toggleVisibility();

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, []);

  useEffect(() => {
    // Alternate between left and right pointing hands every 1.5 seconds
    const interval = setInterval(() => {
      setShowLeftHand((prev) => !prev); // Toggle between true and false
    }, 1500);

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, []);

  useEffect(() => {
    if (state.Active) {
      // Hide pointing hands after the filter is changed
      setPointingVisible(false);
      setPointingUsed(true); // Set the flag to indicate that swiping hand has been used
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
                <div className="bottom-row">
                  {pointingIsVisible && (
                    <div className="bottom_row">
                      {showLeftHand ? (
                        <img
                          src={pointing_hand}
                          id="point_left"
                          style={{ maxWidth: "5%" }}
                        />
                      ) : (
                        <img
                          src={pointing_hand}
                          id="point_right"
                          style={{ maxWidth: "5%" }}
                        />
                      )}
                    </div>
                  )}
                </div>
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

  return <div className="instructions">{renderInstructions()}</div>;
};

export default Instructions;
