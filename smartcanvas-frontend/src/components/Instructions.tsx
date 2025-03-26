/**
 * Component to show different instructions based on the state of the application
 */
import React, {useState, useEffect } from "react";
import waving_hand from "./five_fingers.png"

interface InstructionsProps {
  state: { [key: string]: any };
  countdown: number;
}

const Instructions: React.FC<InstructionsProps> = ({ state, countdown = 0 }) => {
  const [randomColumn, setRandomColumn] = useState<number>(1); // Random column (1, 2, or 3)
  const [isVisible, setIsVisible] = useState<boolean>(true); // Toggle visibility

  // Function to generate a random column ID (1, 2, or 3)
  const getRandomColumn = () => Math.floor(Math.random() * 3) + 1;

  useEffect(() => {
    // Timer to toggle visibility and randomize column every N seconds
    const interval = setInterval(() => {
      setIsVisible((prev) => !prev); // Toggle visibility
      if (!isVisible) {
        setRandomColumn(getRandomColumn()); // Randomize column when becoming visible
      }
    }, 5000);

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, [isVisible]);
  
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
                  {isVisible && randomColumn === 1 && "waving animation"}
                </div>
                <div className="column" id="column-2">
                  {isVisible && randomColumn === 2 && "waving animation"}
                </div>
                <div className="column" id="column-3">
                  {isVisible && randomColumn === 3 && "waving animation"}
                </div>
              </div>
            );
            return <div>Instructions for Idle state
              <img src={waving_hand} style={{maxWidth:'20%', marginLeft:'30%'}} />
            </div>;
          case "Active":
            return (
              <div>
                <div className="top-row">
                  <div className="column" id="column-1"></div>
                  <div className="column" id="column-2"></div>
                  <div className="column" id="column-3">hold palm up</div>
                </div>
                <div className="bottom-row">swipe filters</div>
              </div>
            );
          case "Countdown":
            return (
              <div className="full-container">
                  <div className="big-text">{renderCountdown()}</div>
              </div>
            );
          case "Filter":
            return (
              <div className="full-container">
                show an animation of an artist or paintbrush?
              </div>
            );
          default:
            return <></>;
        }
      }
    }
    return <></>;
  };

  const renderCountdown = () => {
    if (countdown > 0) {
      // Round the countdown up to the nearest integer
      return Math.ceil(countdown);
    }
  };

  return (
    <div className="instructions">
      {/* <h2>
        Current State:{" "}
        {Object.keys(state).find((key) => state[key]) || "Unknown"}
      </h2> */}
      
        {renderInstructions()}
      

    </div>
  );
};

export default Instructions;
