import React from 'react';

function Pipe({ width, height, top, left }) {
  return (
    <div style={{
      position: 'absolute',
      top,
      left,
      width,
      height,
      backgroundColor: '#888'
    }}></div>
  );
}

export default Pipe;
