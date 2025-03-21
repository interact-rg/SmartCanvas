/**
 * This element displays the processed images sent by the server.
 */

import React, { useEffect, useRef } from 'react';

interface ServerFeedProps {
  artisticFrame: string | null;
}

const ServerFeed: React.FC<ServerFeedProps> = ({ artisticFrame }) => {
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
  }, [artisticFrame]);

  return <canvas ref={canvasRef} width={1280} height={720} />;
};

export default ServerFeed;