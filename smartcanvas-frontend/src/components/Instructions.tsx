/**
 * Component to show different instructions based on the state of the application
 */
import React from "react";

interface InstructionsProps {
  state: { [key: string]: any };
}

const Instructions: React.FC<InstructionsProps> = ({ state }) => {
  const renderInstructions = () => {
    for (const [key, value] of Object.entries(state)) {
      if (value) {
        switch (key) {
          case "Startup":
            return <p>Instructions for Startup state</p>;
          case "Idle":
            return <p>Instructions for Idle state</p>;
          case "Active":
            return <p>Instructions for Active state</p>;
          default:
            return <p></p>;
        }
      }
    }
    return <p></p>;
  };

  return (
    <div className="instructions">
      <h2>
        Current State:{" "}
        {Object.keys(state).find((key) => state[key]) || "Unknown"}
      </h2>
      {renderInstructions()}
    </div>
  );
};

export default Instructions;
