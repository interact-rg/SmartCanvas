import React from 'react';

const TopNav: React.FC = () => {
  return (
    <div className="topnav">
      <a className="logo">SmartCanvasV</a>
      <a className="link active" href="">Home</a>
      <a className="link" href="fullscreen">Fullscreen</a>
      <a className="link" href="http://interact.oulu.fi/site/smart-canvas">About</a>
    </div>
  );
};

export default TopNav;