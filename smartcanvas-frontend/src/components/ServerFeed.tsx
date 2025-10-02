/**
 * This element displays the processed images sent by the server.
 */

import React, { useEffect, useRef, useState } from 'react';
import ImagePainter from './ImagePainter';
import '../styles/ServerFeed.css';
import closed_fist from '../assets/closed_fist_shadow.png';
import exit from '../assets/exit.png';

interface ServerFeedProps {
  state: { [key: string]: any };
  artisticFrame: string | null;
  visible: boolean;
  filter: string;
  paintingTimer: number; // Optional prop for painting timer
  needsInstruction: boolean; // Prop to indicate the need for closed fist instruction
}

const ServerFeed: React.FC<ServerFeedProps> = ({ state, artisticFrame, visible = false, filter, paintingTimer, needsInstruction }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [paintingVisible, setPaintingVisible] = useState<boolean>(false);
  const [interrupt, setInterrupt] = useState<boolean>(true); // Flag to interrupt the painting process
  const [ack, setAck] = useState<boolean>(false); // Flag for ImagePainter to ack the interrupt

  useEffect(() => {
    // Check if the artistic frame is available, the canvas is ready and the painting process in not active
    if (!canvasRef.current || !artisticFrame || !state.ShowPic) {
      return;
    }

    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    const image = new Image();
    image.onload = () => {
      // Gradually fade in the artistic frame
      let opacity = 0;
      const fadeIn = () => {
        if (context) {
          context.globalAlpha = opacity; // Set opacity for the artistic frame
          context.drawImage(image, 0, 0, canvas.width, canvas.height);
          opacity += 0.1; // Increment opacity
          if (opacity <= 1) {
            requestAnimationFrame(fadeIn); // Continue fading in
          } else {
            context.globalAlpha = 1; // Ensure full opacity
          }
        }
      };
      fadeIn();
    };

    image.src = `data:image/jpeg;base64,${artisticFrame}`;

    // Cleanup function to clear the canvas on unmount
    return () => {
      if (context) {
        context.clearRect(0, 0, canvas.width, canvas.height);
      }
    };

  }, [artisticFrame, state.ShowPic]);

  useEffect(() => {
    if (!visible) {
      setPaintingVisible(false); // Hide the painting component when not visible
      setInterrupt(true); // Set the interrupt flag to true
      setAck(false); // Reset the ack flag
      const canvas = canvasRef.current;
      if (!canvas) {
        return;
      }
      const context = canvas.getContext('2d');

      // Clear canvas when not visible
      if (context) {
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.globalAlpha = 1; // Reset opacity
      }
    } else {
      if (state.Painting) {
        //setBackground(); // Set the background image
        setInterrupt(false); // Reset the interrupt flag
        setPaintingVisible(true);
      }
      if (state.ShowPic) {
        //console.log("ServerFeed: ShowPic is true, setting interrupt to true.");
        setInterrupt(true); // Set the interrupt flag to true
        console.log("Needs instruction, showPic active: " + needsInstruction +" " + state.ShowPic);
      }
    }
  }, [visible, state]);

  const handleAck = (nack: boolean) => {
    //console.log("Ack received: ", nack);
    setAck(nack); // Update the ack state
    if (ack) {
      setPaintingVisible(false); // Hide the painting component
    }
  }

  return (
    <div className="server-feed">
      {paintingVisible && <ImagePainter canvas={canvasRef.current} filter={filter} interrupt={interrupt} averageTime={paintingTimer} onInterrupt={handleAck} />}
      <canvas ref={canvasRef} width={1280} height={720} className={`canvas ${state.ShowPic ? `artistic-frame` : ''}`} />
      {/* For testing purposes, show image of exit sign and closed fist as an instruction to the user */}
      {(needsInstruction && state.ShowPic) &&
        <div style={{ border: '2px', borderColor: 'black', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', position: 'absolute', top: '10%', right: '1%', height: '10%', width: '10%' }}>
          <img src={exit} id="exit-sign" style={{ maxWidth: '50%'}} />
          <img src={closed_fist} id="closed-fist" style={{ maxWidth: '50%' }} />
        </div>}
    </div>
  );
};

export default ServerFeed;