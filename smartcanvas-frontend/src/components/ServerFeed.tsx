/**
 * This element displays the processed images sent by the server.
 */

import React, { useEffect, useRef } from 'react';
import { Socket } from 'socket.io-client';

interface ServerFeedProps {
  socket: Socket | null;
}

const ServerFeed: React.FC<ServerFeedProps> = ({ socket }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!socket) return;

    socket.on('consume', (msg) => {
      const img = new Image();
      const canvas = canvasRef.current;
      const context = canvas?.getContext('2d');
      img.onload = function () {
        if (context && canvas) {
          context.clearRect(0, 0, canvas.width, canvas.height);
          context.drawImage(img, 0, 0, canvas.width, canvas.height);
        }
      };
      img.src = msg;
    });

    return () => {
      socket.off('consume');
    };
  }, [socket]);

  return <canvas ref={canvasRef} width={1280} height={720} />;
};

export default ServerFeed;