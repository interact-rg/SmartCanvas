import { useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";

const useSocket = (url: string) => {
  const socketRef = useRef<Socket | null>(null);
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    console.log("Initializing socket...");
    const socket = io(url, { reconnection: false });
    socketRef.current = socket;
    setSocket(socket); // Update state when connected

    socket.on("connect", () => {
      console.log("Connected");
    });

    socket.on("disconnect", () => {
      console.log("Disconnected");
      setSocket(null); // Clear state on disconnect
    });

    socket.on("connect_error", (error) => {
      console.log("Connect error! " + error);
    });

    socket.on("connect_timeout", (error) => {
      console.log("Connect timeout! " + error);
    });

    socket.on("error", (error) => {
      console.log("Error! " + error);
    });

    return () => {
      console.log("Cleaning up socket...");
      socket.disconnect();
    };
  }, [url]);

  return socket;
};

export default useSocket;
