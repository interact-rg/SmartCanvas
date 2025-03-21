/**
 * Code to handle socket connection and receive data from the server
 * 
 * */

import React, { useEffect, useState, useRef } from 'react';
//import { Socket } from 'socket.io-client';
import useSocket from '../hooks/useSocket';

interface SocketHandlerProps {
  onStateChange: (state: any) => void;
  videoFrame?: string | null;
  onArtisticFrame: (frame: string) => void;
}

const SocketHandler: React.FC<SocketHandlerProps> = ({ onStateChange, videoFrame, onArtisticFrame }) => {
  const socket = useSocket('http://localhost:5000');
  const [canSendFrame, setCanSendFrame] = useState(true);

  useEffect(() => {
    if (!socket) return;

    // Update the UI state when the server sends a message
    const handleUpdateUIResponse = (msg: any) => {
      //console.log('Received update_ui_response: ', msg);

      // ignore the hold_timer for now
      if (msg.hold_timer !== undefined) {
        console.log('Hold timer: ', msg.hold_timer);
        return;
      } else {
        onStateChange(msg);
      }
    };

    // Handle frame received acknowledgement from the server
    const handleAck = () => {
      //console.log('Received ack, ready to send new frame');
      setCanSendFrame(true);
    };

    // Handle the processed artistic image from the server
    const handleArtisticFrame = (frame: string) => {
      console.log('Received artistic frame from the server: ', frame);
      onArtisticFrame(frame);
    };

    socket.on('ack', handleAck);
    socket.on('update_ui_response', handleUpdateUIResponse);
    socket.on('show_image', handleArtisticFrame);

    return () => {
      socket.off('update_ui_response', handleUpdateUIResponse);
      socket.off('ack', handleAck);
      socket.off('show_image', handleArtisticFrame);
    };
  }, [socket]);

  useEffect(() => {
    // Try to send frame to the server
    const sendFrame = (frame: string) => {
      if (!socket || !canSendFrame) return; // Wait for ack before sending a new frame

      //console.log('Sending frame to the server...');
      socket.emit('produce', frame);
      setCanSendFrame(false); // Prevent sending until ack is received
    };

    if (socket && videoFrame && canSendFrame) {
      sendFrame(videoFrame);
    }
  }, [socket, videoFrame, canSendFrame]);

  return null;
};

export default SocketHandler;