/**
 * Code to handle socket connection and receive data from the server
 * 
 * */

import React, { useEffect, useState, useRef } from 'react';
import useSocket from '../hooks/useSocket';

interface SocketHandlerProps {
  onStateChange: (state: any) => void;
  videoFrame: Blob | null;
  onArtisticFrame: (frame: string) => void;
  onHandPosition: (position: [number, number]) => void;
  onProgress: (progress: number) => void;
  onPainting: (hold: number) => void;
  onFilters: (filters: string[]) => void;
  onChosenFilter: (filter: string) => void;
}

const SocketHandler: React.FC<SocketHandlerProps> = ({ onStateChange, videoFrame, onArtisticFrame, onHandPosition, onProgress, onPainting, onFilters, onChosenFilter }) => {
  const socket = useSocket('http://localhost:5000');
  const [canSendFrame, setCanSendFrame] = useState(true);
  const previousFrameRef = useRef<string | null>(null);

  useEffect(() => {
    if (!socket) return;

    // Handle the list of available filters received from the server
    const handleAvailableFilters = (filters: string[]) => {
      if (filters.length > 0) {
        onFilters(filters);
      }
    };

    // Update the UI state when the server sends a message
    const handleUpdateUIResponse = (msg: any) => {
      console.log('Received update_ui_response: ', msg);

      // Counter to hold your hand still
      if (msg.hold_timer !== undefined) {
        console.log('Hold timer: ', msg.hold_timer);
        onProgress(msg.hold_timer);
        return;
      }
      // Counter to keep still when the image is "being painted"
      else if (msg.timer !== undefined) {
        console.log('Timer: ', msg.timer);
        onPainting(msg.timer);
        return;
      }
      else if (msg.filter !== undefined) {
        console.log('Filter: ', msg.filter);
        onChosenFilter(msg.filter);

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
    socket.on('hand_position', onHandPosition);
    socket.on('available_filters', handleAvailableFilters);

    return () => {
      socket.off('update_ui_response', handleUpdateUIResponse);
      socket.off('ack', handleAck);
      socket.off('show_image', handleArtisticFrame);
      socket.off('hand_position', onHandPosition);
      socket.off('available_filters', handleAvailableFilters);
    };
  }, [socket]);

  useEffect(() => {
    // Try to send frame to the server
    const sendFrame = (frame: Blob) => {
      if (!socket || !canSendFrame) return; // Wait for ack before sending a new frame

      // Convert blob to base64 string
      const reader = new FileReader();
      reader.onloadend = () => {
        const currentFrame = reader.result as string;

        // Compare the current frame with the previous frame to avoid duplicates
        if (currentFrame !== previousFrameRef.current) {
          console.log('Sending frame to the server...');
          socket.emit('produce', currentFrame);
          previousFrameRef.current = currentFrame; // Update the previous frame
          setCanSendFrame(false); // Prevent sending until ack is received
        } else {
          // Frame is identical to the previous one. Skipping.
        }
      };
      reader.readAsDataURL(frame);
    };

    if (socket && videoFrame && canSendFrame) {
      sendFrame(videoFrame);
    }
  }, [socket, videoFrame, canSendFrame]);

  return null;
};

export default SocketHandler;