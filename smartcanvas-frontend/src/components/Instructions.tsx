/**
 * Component to show different instructions based on the state of the application
 */
import React from "react";
import waving_hand from "./five_fingers.png"

interface InstructionsProps {
  state: { [key: string]: any };
}

const Instructions: React.FC<InstructionsProps> = ({ state }) => {
  const renderInstructions = () => {
    for (const [key, value] of Object.entries(state)) {
      if (value) {
        switch (key) {
          case "Startup":
            return <div>Instructions for Startup state</div>;
          case "Idle":
            return <div>Instructions for Idle state
              <img src={waving_hand} style={{maxWidth:'20%', marginLeft:'30%'}} />
            </div>;
          case "Active":
            return <div>Instructions for Active state</div>;
          default:
            return <></>;
        }
      }
    }
    return <></>;
  };

  return (
    <div className="instructions">
      <h2>
        Current State:{" "}
        {Object.keys(state).find((key) => state[key]) || "Unknown"}
      </h2>
      <div>
        {renderInstructions()}
      </div>
      
    </div>
  );
};

export default Instructions;
