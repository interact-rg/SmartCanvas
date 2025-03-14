/**
 * Code to handle socket connection and receive data from the server
 * 
 * */ 

import React, { useEffect, useState } from 'react';
import useSocket from '../hooks/useSocket';

const SocketHandler: React.FC = () => {
  const socket = useSocket('http://localhost:5000');
    console.log(socket);

  return null;
};

export default SocketHandler;