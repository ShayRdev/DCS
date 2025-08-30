import React, { useEffect, useRef } from 'react';

function TransmitterWithGauge({ tag, value, unit, min, max }) {
  const percent = Math.min(Math.max((value - min) / (max - min), 0), 1) * 100;
  const barRef = useRef(null);

  useEffect(() => {
    if (barRef.current) {
      barRef.current.style.width = `${2.4 * percent}px`;
    }
  }, [percent]);

  return (
    <div style={{ marginBottom: '40px' }}>
      <svg width="400" height="120">
        <defs>
          <filter id="softGlow">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>

<radialGradient id="tagShadow" cx="50%" cy="50%" r="70%" fx="50%" fy="50%">
  <stop offset="70%" stopColor="#000" stopOpacity="0.95" />
  <stop offset="40%" stopColor="#000" stopOpacity="0.5" />
  <stop offset="50%" stopColor="#000" stopOpacity="0.5" />
  <stop offset="70%" stopColor="#000" stopOpacity="0.5" />
  <stop offset="90%" stopColor="#000" stopOpacity="0" />
</radialGradient>

<radialGradient id="tagShadow" cx="50%" cy="50%" r="70%" fx="50%" fy="50%">
  <stop offset="0%" stopColor="#000" stopOpacity="0.95" />
  <stop offset="60%" stopColor="#000" stopOpacity="0.5" />
  <stop offset="60%" stopColor="#000" stopOpacity="0.5" />
  <stop offset="100%" stopColor="#000" stopOpacity="0" />
</radialGradient>
        </defs>

        {/* Outer dim circle */}
        <circle cx="60" cy="60" r="42" fill="none" stroke="#033" strokeWidth="3" />

        {/* Neon glow circle */}
        <circle cx="60" cy="60" r="36" fill="none" stroke="#0ff" strokeWidth="4" filter="url(#softGlow)" />

        {/* Inner dim circle */}
        <circle cx="60" cy="60" r="28" fill="#111" />

        {/* Value text */}
        <text x="60" y="56" textAnchor="middle" fontSize="16" fill="#fff" fontWeight="bold">
          {value}
        </text>
        <text x="60" y="72" textAnchor="middle" fontSize="10" fill="#aaa">
          {unit}
        </text>

        {/* Connector tube */}
<path d={`
  M86,60
  C92,50 102,50 112,60
  L360,60
  C370,60 370,80 360,80
  L112,80
  C102,90 92,90 86,60
  Z
`}
fill="#111" stroke="#0ff" strokeWidth="0.75" />


        {/* Gauge fill bar */}
<foreignObject x="114" y="61" width="240" height="18">
          <div style={{
            height: '20px',
            background: 'linear-gradient(to right, #0ff, #0cc)',
            borderRadius: '10px',
            width: '0px',
            transition: 'width 0.5s ease',
            boxShadow: '0 0 10px #0ff',
          }} ref={barRef}></div>
        </foreignObject>

        {/* Gradient tag label backgrounds */}
        <rect x="35" y="83" width="50" height="23" rx="6" fill="url(#tagShadow)" />
        <text x="60" y="95" textAnchor="middle" fontSize="10" fill="#ccc">{tag}</text>

        <rect x="225" y="83" width="50" height="16" rx="6" fill="url(#tagShadow)" />
        <text x="250" y="98" textAnchor="middle" fontSize="10" fill="#ccc">{tag}</text>
      </svg>
    </div>
  );
}

export default TransmitterWithGauge;
