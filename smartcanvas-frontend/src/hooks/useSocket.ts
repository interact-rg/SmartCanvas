import { useEffect, useState, useRef } from "react";
// --- Add necessary types from socket.io-client ---
import { io, Socket, ManagerOptions, SocketOptions } from "socket.io-client";

// Define the type for the options object
type SocketIoOptions = Partial<ManagerOptions & SocketOptions>;
// -------------------------------------------------

let socketInstance: Socket | null = null;

const useSocket = (url: string, options?: SocketIoOptions) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  // Merge default options with passed options
  const mergedOptions = useRef({
    reconnection: false, // Your default
    query: { "version": "alternate" }, // Your default
    ...options // Spread passed options (e.g., path, transports)
  });


  useEffect(() => {
    if (!socketInstance) {
      // --- FIX: Use mergedOptions.current ---
      console.log("Initializing socket with options:", mergedOptions.current);
      socketInstance = io(url, mergedOptions.current);
      // --------------------------------------
    }

    setSocket(socketInstance);

    const handleConnect = () => {
      console.log("Connected");
    };

    const handleDisconnect = () => {
      console.log("Disconnected");
      // Consider if you really want to setSocket(null) here if using a singleton instance
      // setSocket(null);
    };

    const handleError = (error: any) => {
      console.log("Error! " + error);
    };

    const handleConnectError = (error: any) => {
      console.log("Connect error! " + error);
    };

    // connect_timeout is less common, can be removed if not needed
    // const handleConnectTimeout = (error: any) => { ... };

    // Add listeners only if socketInstance exists
    if (socketInstance) {
        socketInstance.on("connect", handleConnect);
        socketInstance.on("disconnect", handleDisconnect);
        socketInstance.on("error", handleError);
        socketInstance.on("connect_error", handleConnectError);
        // socketInstance.on("connect_timeout", handleConnectTimeout);
    }


    return () => {
      console.log("Cleaning up socket listeners...");
      // Remove listeners only if socketInstance exists
      if (socketInstance) {
          socketInstance.off("connect", handleConnect);
          socketInstance.off("disconnect", handleDisconnect);
          socketInstance.off("error", handleError);
          socketInstance.off("connect_error", handleConnectError);
          // socketInstance.off("connect_timeout", handleConnectTimeout);
      }
      // Note: Singleton instance is not disconnected on component unmount here.
    };
  }, [url]); // Dependency array

  return socket;
};

export default useSocket;