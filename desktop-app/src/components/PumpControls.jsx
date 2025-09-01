import React from 'react';

export default function PumpControls({ pump, onRun, onStop, onShowLogs }) {
  const sectionTitle = {
    fontSize: 13,
    color: '#9aa4af',
    textTransform: 'uppercase',
    letterSpacing: '1.4px',
    marginBottom: 6,
  };

  const btn = (active, danger = false) => ({
    display: 'flex',
    gap: 10,
    alignItems: 'center',
    justifyContent: 'center',
    height: 44,
    fontWeight: 700,
    letterSpacing: '0.6px',
    cursor: 'pointer',
    userSelect: 'none',
    borderRadius: 6,
    border: `2px solid ${danger ? '#e04f4f' : active ? '#2bd673' : '#848e9a'}`,
    background: danger
      ? 'linear-gradient(#341616, #2a1212)'
      : active
      ? 'linear-gradient(#193622, #112819)'
      : 'linear-gradient(#171a1e, #14171a)',
    color: danger ? '#ff8e8e' : active ? '#7fffb2' : '#d0d6dc',
    boxShadow: active
      ? '0 0 0 2px rgba(43,214,115,0.12) inset'
      : '0 0 0 2px rgba(255,255,255,0.04) inset',
  });

  const lamp = (on, colorOn, colorOff = '#3a3f45') => ({
    width: 12,
    height: 12,
    borderRadius: 12,
    background: on ? colorOn : colorOff,
    boxShadow: on ? `0 0 10px ${colorOn}` : 'none',
    border: '1px solid #000',
  });

  return (
    <div>
      <div style={sectionTitle}>Pump Controls</div>
      <div style={{ display: 'grid', gap: 10 }}>
        <button style={btn(pump)} onClick={onRun} disabled={pump}>
          <span style={lamp(pump, '#2bd673')} />
          RUN P-101
        </button>
        <button style={btn(false, true)} onClick={onStop} disabled={!pump}>
          <span style={lamp(!pump, '#e04f4f')} />
          STOP P-101
        </button>
        <button
          onClick={onShowLogs}
          style={{
            background: 'none',
            border: 'none',
            color: '#9aa4af',
            cursor: 'pointer',
            fontSize: 13,
            textAlign: 'left',
            padding: 0,
            marginTop: 4,
          }}
        >
          Logs
        </button>
      </div>
    </div>
  );
}
