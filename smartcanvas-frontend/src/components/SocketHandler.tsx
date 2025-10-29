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
  onGesture?: (gesture: string) => void; // ✅ Gesture callback
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
  onGesture,
}) => {
  const serverHostname = window.location.hostname;
  const protocol = window.location.protocol;
  let serverUrl: string;

  if (serverHostname === 'localhost' || serverHostname === '127.0.0.1') {
    serverUrl = `${protocol}//${serverHostname}:5000`;
  } else {
    serverUrl = `${protocol}//${serverHostname}`;
  }

  const isSecure = protocol === 'https:';
  const socket = useSocket(serverUrl, {
    path: "/socket.io/",
    transports: ['websocket', 'polling'],
    secure: isSecure
  });

  const [canSendFrame, setCanSendFrame] = useState(true);
  const previousFrameRef = useRef<string | null>(null);

  useEffect(() => {
    if (!socket) return;

    const handleAvailableFilters = (filters: string[]) => {
      if (filters.length > 0) onFilters(filters);
    };

    const handleUpdateUIResponse = (msg: any) => {
      if (msg.hold_timer !== undefined) {
        onProgress(msg.hold_timer);
        return;
      } else if (msg.timer !== undefined) {
        onHoldStill(msg.timer);
        return;
      } else {
        onStateChange(msg);
      }

      // ✅ Gesture handling
      if (msg.gesture && (msg.gesture === "thumbs_up" || msg.gesture === "thumbs_down")) {
        onGesture?.(msg.gesture);
      }
    };

    const handleAck = () => setCanSendFrame(true);

    const handleFilter = (message: any) => {
      if (message.name) onChosenFilter(message.name);
      if (message.performance) onFilterPerformance(message.performance);
    };

    const handleArtisticFrame = (frame: string) => onArtisticFrame(frame);

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
    };
  }, [socket]);

  useEffect(() => {
    const sendFrame = (frame: Blob) => {
      if (!socket || !canSendFrame) return;
      const reader = new FileReader();
      reader.onloadend = () => {
        const currentFrame = reader.result as string;
        if (currentFrame !== previousFrameRef.current) {
          socket.emit('produce', { currentFrame, baseUrl: window.location.origin });
          previousFrameRef.current = currentFrame;
          setCanSendFrame(false);
        }
      };
      reader.readAsDataURL(frame);
    };

    if (socket && videoFrame && canSendFrame) sendFrame(videoFrame);
  }, [socket, videoFrame, canSendFrame]);

  return null;
};

export default SocketHandler;
