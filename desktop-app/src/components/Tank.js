import React from 'react';

function Tank({ tag, level }) {
  const clamped = Math.max(0, Math.min(100, Number(level) || 0));

  return (
    <div style={{ textAlign: 'center' }}>
      <div
        style={{
          fontFamily: 'IBM Plex Mono, monospace',
          fontSize: 12,
          letterSpacing: '0.12em',
          color: '#8b97a5',
          marginBottom: 10,
        }}
      >
        {tag}
      </div>
      <div
        style={{
          width: 150,
          height: 400,
          margin: '0 auto',
          borderRadius: 10,
          border: '1px solid #2a343e',
          background: 'linear-gradient(180deg, #12171c, #0b0e11)',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.03)',
        }}
      >
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            bottom: 0,
            height: `${clamped}%`,
            background:
              'linear-gradient(180deg, rgba(91,126,166,0.85), rgba(61,184,160,0.75))',
            transition: 'height 0.4s ease',
          }}
        />
        <div
          style={{
            position: 'absolute',
            inset: 12,
            border: '1px dashed #2a343e',
            borderRadius: 6,
            pointerEvents: 'none',
          }}
        />
      </div>
    </div>
  );
}

export default Tank;
