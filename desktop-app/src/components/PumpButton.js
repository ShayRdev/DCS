import React from 'react';

function PumpButton({ pumpStatus, togglePump }) {
  const buttonStyle = {
    backgroundColor: '#007aff',
    border: 'none',
    borderRadius: '10px',
    color: '#fff',
    padding: '10px 20px',
    fontSize: '16px',
    cursor: 'pointer',
    boxShadow: '0 4px 20px rgba(0,122,255,0.4)',
    fontFamily: 'Helvetica Neue, sans-serif',
    marginBottom: '20px'
  };

  return (
    <button style={buttonStyle} onClick={togglePump}>
      {pumpStatus ? 'Stop Pump' : 'Start Pump'}
    </button>
  );
}

export default PumpButton;
