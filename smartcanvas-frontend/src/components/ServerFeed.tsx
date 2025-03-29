/**
 * This element displays the processed images sent by the server.
 */

import React, { useEffect, useRef } from 'react';

interface ServerFeedProps {
  artisticFrame: string | null;
  visible: boolean;
}

const ServerFeed: React.FC<ServerFeedProps> = ({ artisticFrame, visible = false }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || !artisticFrame) {
      return;
    }

    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    const image = new Image();
    image.onload = () => {
      context?.drawImage(image, 0, 0, canvas.width, canvas.height);
    };

    image.src = `data:image/jpeg;base64,${artisticFrame}`;

    // Cleanup function to clear the canvas on unmount
    return () => {
      if (context) {
        context.clearRect(0, 0, canvas.width, canvas.height);
      }
    };

  }, [artisticFrame]);

  useEffect(() => {
    if (visible === false) {
      const canvas = canvasRef.current;
      if (!canvas) {
        return;
      }
      const context = canvas.getContext('2d');
      
      // Clear canvas when not visible
      if (context) {
        context.clearRect(0, 0, canvas.width, canvas.height);
      }
    }
  }, [visible]);


  return (
    <div className="server-feed">
      {/* TODO: create an awesome frame around the image at some point */}
      <canvas ref={canvasRef} width={1280} height={720} />
    </div>
  );
};

export default ServerFeed;