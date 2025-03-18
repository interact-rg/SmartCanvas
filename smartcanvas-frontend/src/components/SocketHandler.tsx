/**
 * Code to handle socket connection and receive data from the server
 * 
 * */

import React, { useEffect } from 'react';
import { Socket } from 'socket.io-client';

interface SocketHandlerProps {
  socket: Socket | null;
  onStateChange: (state: any) => void;
}

const SocketHandler: React.FC<SocketHandlerProps> = ({ socket, onStateChange }) => {

  useEffect(() => {
    if (!socket) return;
    socket.on('update_ui_response', (msg) => {
      console.log('Received update_ui_response: ', msg);
      // ignore the hold_timer for now
      if (msg.hold_timer !== undefined) {
        return;
      } else {
        onStateChange(msg);
      }
      
    });

  }, [socket, onStateChange]);

  return null;
};

export default SocketHandler;