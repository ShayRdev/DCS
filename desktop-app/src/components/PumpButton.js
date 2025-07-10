import React from 'react';

function PumpButton({ pumpStatus, togglePump }) {
  const buttonStyle = {
    padding: '10px 20px',
    fontSize: '16px',
    backgroundColor: '#333',
    color: '#fff',
    border: '2px solid #555',
    borderRadius: '5px',
    cursor: 'pointer',
    marginBottom: '10px'
  };

  return (
    <div style={{ textAlign: 'center' }}>
      <button onClick={togglePump} style={buttonStyle}>
        {pumpStatus ? "Stop Pump" : "Start Pump"}
      </button>
      <div style={{ fontSize: '16px', marginTop: '10px' }}>
        <strong>Pump Status:</strong> {pumpStatus ? "ON" : "OFF"}
      </div>
    </div>
  );
}

export default PumpButton;
