import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import Tank from './components/Tank';
import Instrument from './components/Instrument';

const DEFAULT_WS =
  process.env.REACT_APP_LOOP_MONITOR_WS_URL ||
  `ws://${window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? '127.0.0.1' : '192.168.1.125'}:8765`;

const MAX_LOG = 40;

function parseReading(raw) {
  const text = String(raw);
  try {
    const msg = JSON.parse(text);
    if (msg && typeof msg === 'object') {
      if (msg.type === 'reading' || typeof msg.temperature_c === 'number') {
        return {
          temperature: Number(msg.temperature_c),
          voltage: Number(msg.voltage_v),
          current: Number(msg.current_ma),
          pump: msg.pump === 'on',
          kind: 'reading',
        };
      }
      if (msg.type === 'pump') {
        return { pump: msg.pump === 'on', kind: 'pump' };
      }
      if (typeof msg.temperature === 'number' || typeof msg.temperature === 'string') {
        return {
          temperature: Number(msg.temperature),
          kind: 'reading',
        };
      }
    }
  } catch {
    /* plain number from older Pi publishers */
  }
  const n = Number.parseFloat(text);
  if (!Number.isNaN(n)) return { temperature: n, kind: 'reading' };
  return null;
}

function Dashboard() {
  const [wsUrl, setWsUrl] = useState(DEFAULT_WS);
  const [connected, setConnected] = useState(false);
  const [reconnecting, setReconnecting] = useState(false);
  const [hadLink, setHadLink] = useState(false);
  const [temperature, setTemperature] = useState(null);
  const [voltage, setVoltage] = useState(null);
  const [current, setCurrent] = useState(null);
  const [pumpStatus, setPumpStatus] = useState(false);
  const [level, setLevel] = useState(28);
  const [flow, setFlow] = useState(0);
  const [pressure, setPressure] = useState(0);
  const [logLines, setLogLines] = useState([]);
  const [clock, setClock] = useState(() => new Date());
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);

  const pushLog = useCallback((line) => {
    setLogLines((prev) => {
      const next = [...prev, { id: `${Date.now()}-${Math.random()}`, text: line }];
      return next.slice(-MAX_LOG);
    });
  }, []);

  useEffect(() => {
    const id = setInterval(() => setClock(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    let closed = false;
    let backoff = 600;
    let linkedOnce = false;
    setConnected(false);
    setReconnecting(false);
    setHadLink(false);

    const scheduleReconnect = () => {
      if (closed) return;
      setReconnecting(true);
      clearTimeout(reconnectRef.current);
      reconnectRef.current = setTimeout(connect, backoff);
      backoff = Math.min(backoff * 1.7, 8000);
    };

    const connect = () => {
      if (closed) return;
      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          const wasLost = linkedOnce;
          setConnected(true);
          setReconnecting(false);
          setHadLink(true);
          linkedOnce = true;
          backoff = 600;
          pushLog(wasLost ? `reconnected ${wsUrl}` : `connected ${wsUrl}`);
        };

        ws.onmessage = (event) => {
          const parsed = parseReading(event.data);
          if (!parsed) return;
          if (parsed.kind === 'pump' || typeof parsed.pump === 'boolean') {
            if (typeof parsed.pump === 'boolean') setPumpStatus(parsed.pump);
          }
          if (parsed.kind === 'reading') {
            if (typeof parsed.temperature === 'number' && !Number.isNaN(parsed.temperature)) {
              setTemperature(parsed.temperature);
            }
            if (typeof parsed.voltage === 'number' && !Number.isNaN(parsed.voltage)) {
              setVoltage(parsed.voltage);
            }
            if (typeof parsed.current === 'number' && !Number.isNaN(parsed.current)) {
              setCurrent(parsed.current);
            }
            const t =
              typeof parsed.temperature === 'number' ? parsed.temperature.toFixed(2) : '--';
            const i =
              typeof parsed.current === 'number' ? `${parsed.current.toFixed(3)} mA` : '';
            const v =
              typeof parsed.voltage === 'number' ? `${parsed.voltage.toFixed(4)} V` : '';
            pushLog(`TT  ${t} °C   ${i}   ${v}`.trim());
          }
        };

        ws.onclose = () => {
          setConnected(false);
          if (linkedOnce) {
            pushLog('Pi link lost — retrying…');
          }
          scheduleReconnect();
        };

        ws.onerror = () => {
          try {
            ws.close();
          } catch {
            /* ignore */
          }
        };
      } catch (err) {
        setConnected(false);
        scheduleReconnect();
      }
    };

    connect();
    return () => {
      closed = true;
      clearTimeout(reconnectRef.current);
      try {
        wsRef.current && wsRef.current.close();
      } catch {
        /* ignore */
      }
    };
  }, [wsUrl, pushLog]);

  // Local process animation (tank/pump) — same idea as the original dashboard.
  // Temperature itself comes from the Pi / simulator, not this ticker.
  useEffect(() => {
    const id = setInterval(() => {
      setLevel((prev) => {
        if (pumpStatus) return Math.min(prev + 0.12, 100);
        return Math.max(prev - 0.06, 0);
      });
      setFlow(pumpStatus ? 50 : 0);
      setPressure(pumpStatus ? 15 : 0);
    }, 500);
    return () => clearInterval(id);
  }, [pumpStatus]);

  const togglePump = () => {
    const next = !pumpStatus;
    setPumpStatus(next);
    const msg = JSON.stringify({ command: 'pump', state: next ? 'on' : 'off', gpio: 17 });
    try {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(msg);
      }
    } catch {
      /* ignore */
    }
  };

  const tempDisplay = useMemo(() => {
    if (temperature == null || Number.isNaN(temperature)) return '—';
    return temperature.toFixed(1);
  }, [temperature]);

  const tapHeightPercent = 20;
  const ltLevel =
    level < tapHeightPercent ? 0 : ((level - tapHeightPercent) * 27.68) / 100;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">Loop Monitor</div>
          <div className="brand-sub">Pi · 4–20 mA</div>
        </div>
        <div className="topbar-meta">
          <div
            className={`conn ${connected ? 'live' : 'lost'}`}
            title={wsUrl}
            role="status"
            aria-live="polite"
          >
            <span className={`conn-dot ${connected ? 'ok' : ''}`} />
            {connected
              ? 'Pi link live'
              : hadLink
                ? 'Pi link lost'
                : reconnecting
                  ? 'Pi link connecting…'
                  : 'Pi link connecting…'}
          </div>
          <span>{clock.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
        </div>
      </header>

      {!connected && (
        <div className="link-banner" role="alert">
          {hadLink
            ? 'Pi link lost — desktop is blind until reconnect. The Pi keeps sampling locally.'
            : 'Connecting to Pi WebSocket…'}
        </div>
      )}

      <main className="layout">
        <aside className="panel">
          <h2>Rosemount TT-103</h2>
          <div className="temp-hero">
            <div className="temp-value">
              {tempDisplay}
              <span>°C</span>
            </div>
            <div className="temp-tag">ADS1115 AIN0 · 250 Ω · 4–20 mA loop</div>
          </div>

          <div className="metrics">
            <div className="metric">
              <label>Loop current</label>
              <strong>{current == null ? '—' : `${current.toFixed(3)} mA`}</strong>
            </div>
            <div className="metric">
              <label>Shunt voltage</label>
              <strong>{voltage == null ? '—' : `${voltage.toFixed(4)} V`}</strong>
            </div>
          </div>

          <h2>Terminal readout</h2>
          <div className="terminal" aria-live="polite">
            {logLines.length === 0 && <div>waiting for readings…</div>}
            {logLines.map((line, idx) => (
              <div
                key={line.id}
                className={idx === logLines.length - 1 ? 'line-new' : undefined}
              >
                {line.text}
              </div>
            ))}
          </div>

          <button
            type="button"
            className={`pump-btn ${pumpStatus ? 'on' : ''}`}
            onClick={togglePump}
          >
            {pumpStatus ? 'Stop pump' : 'Start pump'}
          </button>

          <p className="hint">
            Point the app at your Pi WebSocket (default <code>{DEFAULT_WS}</code>).
            Override with <code>REACT_APP_LOOP_MONITOR_WS_URL</code>.
            <br />
            <label htmlFor="ws-url" style={{ display: 'inline-block', marginTop: 8 }}>
              WS URL{' '}
              <input
                id="ws-url"
                value={wsUrl}
                onChange={(e) => setWsUrl(e.target.value.trim())}
                style={{
                  marginLeft: 6,
                  width: '100%',
                  maxWidth: 280,
                  marginTop: 4,
                  background: '#07090b',
                  border: '1px solid #2a343e',
                  color: '#e8edf2',
                  padding: '6px 8px',
                  borderRadius: 4,
                  fontFamily: 'IBM Plex Mono, monospace',
                  fontSize: '0.75rem',
                }}
              />
            </label>
          </p>
        </aside>

        <section className="panel process">
          <h2>Process view</h2>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'minmax(160px, 200px) 1fr',
              gap: 24,
              alignItems: 'start',
            }}
          >
            <Tank tag="T-G-122" level={Math.max(level, 8)} />
            <div className="instruments">
              <Instrument tag="PT-102" value={pressure} unit="psi" min={0} max={30} />
              <Instrument
                tag="TT-103"
                value={temperature == null ? 0 : temperature}
                unit="°C"
                min={0}
                max={100}
                accent
              />
              <Instrument tag="FT-104" value={flow} unit="gpm" min={0} max={100} />
              <Instrument tag="LT-101" value={ltLevel} unit="inH₂O" min={0} max={30} />
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default Dashboard;
