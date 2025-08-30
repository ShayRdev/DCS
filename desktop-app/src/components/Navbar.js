import React from 'react';

function Navbar({ temperature, humidity, site }) {
  const navbarStyle = {
    width: '100%',
    backgroundColor: '#1c1c1e',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 40px', // increased from 30px to 40px for more side spacing
    color: '#fff',
    fontFamily: 'Helvetica Neue, sans-serif',
    fontWeight: 500,
    fontSize: '14px',
    boxShadow: '0 2px 6px rgba(0,0,0,0.7)',
    borderBottom: '1px solid #333',
    letterSpacing: '0.5px',
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
    boxSizing: 'border-box' // ensure padding is inside width
  };

  const rightSideStyle = {
    display: 'flex',
    gap: '20px',
    alignItems: 'center',
    flexWrap: 'nowrap'
  };

  const iconStyle = {
    fontSize: '14px',
    marginRight: '5px',
    color: '#0f0'
  };

  const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <div style={navbarStyle}>
      <div style={{ fontSize: '16px' }}>{site || "Plant Monitoring Dashboard"}</div>
      <div style={rightSideStyle}>
        <div><span style={iconStyle}>🌡</span>{temperature}°C</div>
        <div><span style={iconStyle}>💧</span>{humidity}% RH</div>
        <div><span style={iconStyle}>🕒</span>{currentTime}</div>
      </div>
    </div>
  );
}

export default Navbar;
