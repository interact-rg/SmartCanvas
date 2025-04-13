// Basic listeners for the socket connection

import { useEffect, useState } from "react";
import { io, Socket } from "socket.io-client";

let socketInstance: Socket | null = null;

const useSocket = (url: string, options?: SocketIoOptions) => {
  // --------------------------------------
    const [socket, setSocket] = useState<Socket | null>(null);
    // Merge default options with passed options
    const mergedOptions = useRef({
      reconnection: false, // Your default
      query: { "version": "alternate" }, // Your default
      ...options // Spread passed options (e.g., path, transports)
    });
  

  useEffect(() => {
    if (!socketInstance) {
      console.log("Initializing socket...");
      socketInstance = io(url, { reconnection: false, query: { "version": "alternate" } });
    }

    setSocket(socketInstance);

    const handleConnect = () => {
      console.log("Connected");
    };

    const handleDisconnect = () => {
      console.log("Disconnected");
      setSocket(null); // Clear state on disconnect
    };

    const handleError = (error: any) => {
      console.log("Error! " + error);
    };

    const handleConnectError = (error: any) => {
      console.log("Connect error! " + error);
    };

    const handleConnectTimeout = (error: any) => {
      console.log("Connect timeout! " + error);
    };

    socketInstance.on("connect", handleConnect);
    socketInstance.on("disconnect", handleDisconnect);
    socketInstance.on("error", handleError);
    socketInstance.on("connect_error", handleConnectError);
    socketInstance.on("connect_timeout", handleConnectTimeout);

    return () => {
      console.log("Cleaning up socket...");
      socketInstance?.off("connect", handleConnect);
      socketInstance?.off("disconnect", handleDisconnect);
      socketInstance?.off("error", handleError);
      socketInstance?.off("connect_error", handleConnectError);
      socketInstance?.off("connect_timeout", handleConnectTimeout);
    };
  }, [url]);

  return socket;
};

export default useSocket;