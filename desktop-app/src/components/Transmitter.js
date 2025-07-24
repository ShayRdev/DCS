import React from 'react';

function Transmitter({ tag, value, unit }) {
  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    margin: '10px',
    background: '#111',
    borderRadius: '15px',
    padding: '10px 20px',
    boxShadow: '0 0 20px rgba(0, 255, 255, 0.4), 0 0 40px rgba(0, 255, 255, 0.2) inset',
    border: '2px solid #0ff',
    color: '#0ff',
    fontFamily: '"Orbitron", sans-serif'
  };

  const valueStyle = {
    fontSize: '28px',
    fontWeight: 'bold',
    textShadow: '0 0 8px #0ff'
  };

  const unitStyle = {
    fontSize: '14px',
    marginTop: '-5px',
    color: '#7fffff'
  };

  const tagStyle = {
    fontSize: '12px',
    marginTop: '5px',
    color: '#0ff',
    opacity: 0.8
  };

  return (
    <div style={containerStyle}>
      <div style={valueStyle}>{value}</div>
      <div style={unitStyle}>{unit}</div>
      <div style={tagStyle}>{tag}</div>
    </div>
  );
}

export default Transmitter;
