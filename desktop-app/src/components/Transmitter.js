import React from 'react';

function Transmitter({ tag, value, unit }) {
  return (
    <div style={{
      backgroundColor: '#333',
      borderRadius: '50%',
      width: '80px',
      height: '80px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      boxShadow: '2px 2px 8px rgba(0,0,0,0.6)',
      border: '2px solid #555',
      fontSize: '10px'
    }}>
      <div style={{
        backgroundColor: '#000',
        color: '#0f0',
        borderRadius: '3px',
        width: '50px',
        height: '20px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        fontSize: '10px'
      }}>
        {value} {unit}
      </div>
      <div style={{ marginTop: '2px', color: '#ccc' }}>{tag}</div>
    </div>
  );
}

export default Transmitter;
