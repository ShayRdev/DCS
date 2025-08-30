import React from 'react';

function Tank({ tag, level }) {
  const tankContainer = {
    width: '150px',
    height: '400px',
    borderRadius: '20px',
    backgroundColor: '#111',
    boxShadow: '0 0 20px #00f, 0 0 40px #00f inset',
    border: '2px solid #0ff',
    position: 'relative',
    overflow: 'hidden'
  };

  const fluidStyle = {
    position: 'absolute',
    bottom: 0,
    left: 0,
    width: '100%',
    height: `${level}%`,
    background: 'linear-gradient(to top, #00f, #00f)',
    boxShadow: '0 0 10px #00f'
  };

  const tagStyle = {
    textAlign: 'center',
    marginBottom: '10px',
    color: '#0ff',
    textShadow: '0 0 5px #0ff'
  };

  return (
    <div style={{ textAlign: 'center' }}>
      <div style={tagStyle}>{tag}</div>
      <div style={tankContainer}>
        <div style={fluidStyle}></div>
      </div>
    </div>
  );
}

export default Tank;
