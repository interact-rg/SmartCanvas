/**
 * This element displays the processed images sent by the server.
 */

import React, { useEffect, useRef, useState } from 'react';
import ImagePainter from './ImagePainter';
import backgroundImg from '../assets/canvas.jpg';

interface ServerFeedProps {
  state: { [key: string]: any };
  artisticFrame: string | null;
  visible: boolean;
  filter: string;
}

const ServerFeed: React.FC<ServerFeedProps> = ({ state, artisticFrame, visible = false, filter }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [paintingVisible, setPaintingVisible] = useState<boolean>(false);
  const [interrupt, setInterrupt] = useState<boolean>(true); // Flag to interrupt the painting process

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
        setInterrupt(true); // Set the interrupt flag to true
        //setPaintingVisible(false); // Hide the painting component when ShowPic is true
      }
    }
  }, [visible, state]);

  function setBackground() {
    // TODO: make this work
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }
    const context = canvas.getContext('2d');
    const background = new Image();
    background.src = backgroundImg;
    context?.clearRect(0, 0, canvas.width, canvas.height);
    context?.drawImage(background, 0, 0, canvas.width, canvas.height);
  }

  return (
    <div className="server-feed">
      {/* TODO: create an awesome frame around the image at some point */}
      {paintingVisible && <ImagePainter canvas={canvasRef.current} filter={filter} interrupt={interrupt} />}
      <canvas ref={canvasRef} width={1280} height={720} />
    </div>
  );
};

export default ServerFeed;