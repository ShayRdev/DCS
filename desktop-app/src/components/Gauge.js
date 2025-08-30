import React from 'react';

function Gauge({ value, min, max, unit }) {
  const percentage = ((value - min) / (max - min)) * 100;
  const clamped = Math.max(0, Math.min(percentage, 100));

  const gaugeContainer = {
    width: '240px', // increased from 80px to 240px
    height: '20px',
    background: '#444',
    borderRadius: '10px',
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'row',
    marginLeft: '10px',
    boxShadow: 'inset 0 0 5px rgba(0,0,0,0.7)'
  };

  const fillStyle = {
    width: `${clamped}%`,
    height: '100%',
    backgroundColor: clamped < 70 ? '#0f0' : clamped < 90 ? '#ff0' : '#f00',
    transition: 'width 0.3s'
  };

  const labelStyle = {
    fontSize: '10px',
    color: '#ccc',
    textAlign: 'center',
    marginTop: '4px'
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div style={gaugeContainer}>
        <div style={fillStyle}></div>
      </div>
      <div style={labelStyle}>{min} - {max} {unit}</div>
    </div>
  );
}

export default Gauge;
