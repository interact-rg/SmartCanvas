/**
 * Code to handle socket connection and receive data from the server
 * 
 * */ 

import React, { useEffect, useState } from 'react';
import { Socket } from 'socket.io-client';

interface SocketHandlerProps {
    socket: Socket | null;
  }

const SocketHandler: React.FC<SocketHandlerProps> = ({ socket }) => {

    console.log(socket);

  return null;
};

export default SocketHandler;