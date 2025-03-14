/**
 * Navigation bar at the top of the page.
 * Non-textual version does not use this element.
 */

import React from 'react';
import './style.css'

const TopNav: React.FC = () => {
  return (
    <div className="topnav">
      <a className="logo">SmartCanvas</a>
      <a className="link active" href="">Home</a>
      <a className="link" href="fullscreen">Fullscreen</a>
      <a className="link" href="http://interact.oulu.fi/site/smart-canvas">About</a>
    </div>
  );
};

export default TopNav;