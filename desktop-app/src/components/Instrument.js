import React from 'react';

function Instrument({ tag, value, unit, min = 0, max = 100, accent = false }) {
  const n = Number(value);
  const safe = Number.isFinite(n) ? n : 0;
  const pct = Math.max(0, Math.min(100, ((safe - min) * 100) / (max - min || 1)));
  const label = Number.isFinite(n) ? (Math.abs(n) >= 100 ? n.toFixed(0) : n.toFixed(1)) : '—';

  return (
    <div className="instrument">
      <div
        className="instrument-dial"
        style={accent ? { borderColor: '#e8a14a' } : undefined}
      >
        <strong style={accent ? { color: '#e8a14a' } : undefined}>{label}</strong>
      </div>
      <div className="instrument-body">
        <div className="instrument-tag">
          {tag} · {unit}
        </div>
        <div className="instrument-bar">
          <div
            className="instrument-fill"
            style={{
              width: `${pct}%`,
              background: accent
                ? 'linear-gradient(90deg, #a06d2c, #e8a14a)'
                : undefined,
            }}
          />
        </div>
      </div>
    </div>
  );
}

export default Instrument;
