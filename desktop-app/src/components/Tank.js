import React from 'react';

function Tank({ tag, level }) {
  const tankContainer = {
    width: '150px',
    height: '400px',
    border: '4px solid #555',
    borderRadius: '10px',
    overflow: 'hidden',
    backgroundColor: '#333',
    position: 'relative'
  };

  const fluidStyle = {
    position: 'absolute',
    bottom: 0,
    width: '100%',
    height: `${level}%`,
    backgroundColor: '#1E90FF',
    transition: 'height 0.5s'
  };

  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{tag}</div>
      <div style={tankContainer}>
        <div style={fluidStyle}></div>
      </div>
    </div>
  );
}

export default Tank;
