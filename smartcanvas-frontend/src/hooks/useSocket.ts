import { useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';

const useSocket = (url: string) => {
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    const socket = io(url, { reconnection: false });
    socketRef.current = socket;

    socket.on('connect', () => {
      console.log('Connected');
    });

    socket.on('disconnect', () => {
      console.log('Disconnected');
    });

    socket.on('connect_error', (error) => {
      console.log('Connect error! ' + error);
    });

    socket.on('connect_timeout', (error) => {
      console.log('Connect timeout! ' + error);
    });

    socket.on('error', (error) => {
      console.log('Error! ' + error);
    });

    return () => {
      socket.disconnect();
    };
  }, [url]);

  return socketRef.current;
};

export default useSocket;