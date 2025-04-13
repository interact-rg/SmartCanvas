
import React, { useEffect, useState, useRef } from 'react';
import useSocket from '../hooks/useSocket';

interface SocketHandlerProps {
  onStateChange: (state: any) => void;
  videoFrame: Blob | null;
  onArtisticFrame: (frame: string) => void;
  onHandPosition: (position: [number, number]) => void;
  onProgress: (progress: number) => void;
  onHoldStill: (timer: number) => void;
  onFilters: (filters: string[]) => void;
  onChosenFilter: (filter: string) => void;
  onFilterPerformance: (performance: number) => void;
  onQrCode: (qrCode: string) => void;
}

const SocketHandler: React.FC<SocketHandlerProps> = ({
  onStateChange,
  videoFrame,
  onArtisticFrame,
  onHandPosition,
  onProgress,
  onHoldStill,
  onFilters,
  onChosenFilter,
  onFilterPerformance,
  onQrCode,
}) => {
  // CHANGED LINE: use same origin + /socket.io path instead of localhost:5000
  const socket = useSocket(`${window.location.origin}/socket.io`);

  const [canSendFrame, setCanSendFrame] = useState(true);
  const previousFrameRef = useRef<string | null>(null);

  useEffect(() => {
    if (!socket) return;

    // Handle the list of available filters
    const handleAvailableFilters = (filters: string[]) => {
      if (filters.length > 0) {
        onFilters(filters);
      }
    };

    // Update the UI state
    const handleUpdateUIResponse = (msg: any) => {
      if (msg.hold_timer !== undefined) {
        onProgress(msg.hold_timer);
      } else if (msg.timer !== undefined) {
        onHoldStill(msg.timer);
      } else {
        onStateChange(msg);
      }
    };

    // Ack from server
    const handleAck = () => {
      setCanSendFrame(true);
    };

    // Filter info
    const handleFilter = (message: any) => {
      if (message.name) {
        onChosenFilter(message.name);
      }
      if (message.performance) {
        onFilterPerformance(message.performance);
      }
    };

    // Artistic frame from server
    const handleArtisticFrame = (frame: string) => {
      onArtisticFrame(frame);
    };

    socket.on('ack', handleAck);
    socket.on('update_ui_response', handleUpdateUIResponse);
    socket.on('show_image', handleArtisticFrame);
    socket.on('hand_position', onHandPosition);
    socket.on('available_filters', handleAvailableFilters);
    socket.on('qr_code', onQrCode);
    socket.on('filter', handleFilter);

    return () => {
      socket.off('update_ui_response', handleUpdateUIResponse);
      socket.off('ack', handleAck);
      socket.off('show_image', handleArtisticFrame);
      socket.off('hand_position', onHandPosition);
      socket.off('available_filters', handleAvailableFilters);
      socket.off('qr_code', onQrCode);
      socket.off('filter', handleFilter);
    };
  }, [socket]);

  useEffect(() => {
    const sendFrame = (frame: Blob) => {
      if (!socket || !canSendFrame) return;

      // Convert blob to base64
      const reader = new FileReader();
      reader.onloadend = () => {
        const currentFrame = reader.result as string;
        if (currentFrame !== previousFrameRef.current) {
          socket.emit('produce', currentFrame);
          previousFrameRef.current = currentFrame;
          setCanSendFrame(false);
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