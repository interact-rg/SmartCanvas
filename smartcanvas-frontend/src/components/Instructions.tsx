/**
 * Component to show different instructions based on the state of the application
 */
import React, {useState, useEffect } from "react";
import waving_hand from "../assets/five_fingers.png"
import "../styles/hand.css"
import swiping_hand from "../assets/swiping_hand.png"
import ImagePainter from "./ImagePainter";

interface InstructionsProps {
  state: { [key: string]: any };
  countdown: number;
  filter: string;
}

const Instructions: React.FC<InstructionsProps> = ({ state, countdown = 4, filter }) => {
  const [randomColumn, setRandomColumn] = useState<number>(1); // Random column (1, 2, or 3)
  const [waveIsVisible, setWaveIsVisible] = useState<boolean>(true); // Toggle visibility of the waving hand
  const [swipeIsVisible, setSwipeVisible] = useState<boolean>(true); //instructions (swiping_hand) should be invisible for n seconds after filter is changed (user has learned how to switch filters, so instructions don't need to be visible)

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

  useEffect (() => {
    if (state.Idle) {
      setSwipeVisible(true); // Reset swiping hand visibility when Idle state is active
    }    
  }, [state]);

  useEffect(() => {
    if (state.Active) {
      // Hide swiping hand after the filter is changed
      setSwipeVisible(false);
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
                  {waveIsVisible && randomColumn === 1 && <img src={waving_hand} id="hand" style={{maxWidth:'20%', marginLeft:'30%'}} />}
                </div>
                <div className="column" id="column-2">
                  {waveIsVisible && randomColumn === 2 && <img src={waving_hand} id="hand" style={{maxWidth:'20%', marginLeft:'30%'}} />}
                </div>
                <div className="column" id="column-3">
                  {waveIsVisible && randomColumn === 3 && <img src={waving_hand} id="hand" style={{maxWidth:'20%', marginLeft:'30%'}} />}
                </div>
              </div>
            );
          case "Active":
            return (
              <div className="instructions">
                <div className="top-row">
                  <div className="column" id="column-1"></div>
                  <div className="column" id="column-2">{swipeIsVisible && <img src={swiping_hand} id="two_fingers_icon" style={{maxWidth: '20%'}}  />}</div>
                  <div className="column" id="column-3">hold palm up</div>
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
          case "Painting":
            return (
              <div className="full-container">
                <img src="/images/canvas.jpg"></img>
                <ImagePainter filter={filter || "painterly"} />
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

  const hideSwipingHand = () => {
    setSwipeVisible((prev) => !prev);
    console.log("swiping_hand set invisible (should be false): " + swipeIsVisible)
    setTimeout( function () {
      console.log("swiping_hand set invisible (should be false): " + swipeIsVisible)
      setSwipeVisible((prev) => !prev);
      console.log("Swiping hand visible (should be true): " + swipeIsVisible)
    }, 5000);
    
  }

  return (
    <div className="instructions">
      
        {renderInstructions()}
      
    </div>
  );
};

export default Instructions;
