import React from 'react';

function Pipe({ x1, y1, x2, y2, color }) {
  const pipeColor = color === "blue" ? "#00f6ff" : color === "red" ? "#ff4d4d" : "#888";

  return (
    <line
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke={pipeColor}
      strokeWidth="4"
      strokeLinecap="round"
      filter="url(#neon-glow)"
    />
  );
}

export default Pipe;
