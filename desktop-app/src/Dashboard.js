// DCSDashboard.jsx
import React, { useEffect, useMemo, useRef, useState } from "react";

/** ======== CONFIG ======== */
const WS_URL = "ws://192.168.1.125:8765"; // <-- change if your Pi IP changes
const POLL_MS = 500;                       // simulation tick
const LOW_LEVEL = 10;                      // % threshold for low-level alarm
const CLEAR_LEVEL = LOW_LEVEL + 2;         // alarm considered cleared above this %

/** ======== STYLES (DCS-ish) ======== */
const appStyle = {
  display: "grid",
  gridTemplateRows: "48px 1fr 68px",
  gridTemplateColumns: "260px 1fr 360px",
  gridTemplateAreas: `
    "topbar topbar topbar"
    "left   main   right"
    "alarms alarms alarms"
  `,
  minHeight: "100vh",
  background: "#101214",
  color: "#e7e7e7",
  fontFamily: "Roboto Mono, Menlo, ui-monospace, monospace",
};

const bar = {
  background: "#1b1e22",
  borderBottom: "2px solid #32373e",
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: "0 12px",
  letterSpacing: "0.3px",
};

const panelBase = {
  background: "#15181b",
  border: "2px solid #32373e",
  borderRadius: 4,
  padding: 12,
};

const leftPanel  = { ...panelBase, gridArea: "left",  display: "grid", gap: 12 };
const rightPanel = { ...panelBase, gridArea: "right", display: "grid", gap: 12, gridTemplateColumns: "1fr" };
const mainPanel  = { ...panelBase, gridArea: "main",  position: "relative", overflow: "hidden" };

const alarmBar = {
  gridArea: "alarms",
  background: "#1b1e22",
  borderTop: "2px solid #32373e",
  display: "flex",
  alignItems: "center",
  gap: 16,
  padding: "8px 12px",
  fontSize: 14,
};

const statusPill = (ok) => ({
  padding: "4px 10px",
  borderRadius: 12,
  border: `1px solid ${ok ? "#2d5" : "#f55"}`,
  color: ok ? "#2d5" : "#f55",
  background: ok ? "rgba(45,213,90,0.08)" : "rgba(255,85,85,0.08)",
});

const sectionTitle = {
  fontSize: 13,
  color: "#9aa4af",
  textTransform: "uppercase",
  letterSpacing: "1.4px",
  marginBottom: 6,
};

const btn = (active, danger = false) => ({
  display: "flex",
  gap: 10,
  alignItems: "center",
  justifyContent: "center",
  height: 44,
  fontWeight: 700,
  letterSpacing: "0.6px",
  cursor: "pointer",
  userSelect: "none",
  borderRadius: 6,
  border: `2px solid ${danger ? "#e04f4f" : active ? "#2bd673" : "#848e9a"}`,
  background: danger
    ? "linear-gradient(#341616, #2a1212)"
    : active
    ? "linear-gradient(#193622, #112819)"
    : "linear-gradient(#171a1e, #14171a)",
  color: danger ? "#ff8e8e" : active ? "#7fffb2" : "#d0d6dc",
  boxShadow: active
    ? "0 0 0 2px rgba(43,214,115,0.12) inset"
    : "0 0 0 2px rgba(255,255,255,0.04) inset",
});

const lamp = (on, colorOn, colorOff = "#3a3f45") => ({
  width: 12,
  height: 12,
  borderRadius: 12,
  background: on ? colorOn : colorOff,
  boxShadow: on ? `0 0 10px ${colorOn}` : "none",
  border: "1px solid #000",
});

/** ======== SIMPLE INSTRUMENT PANEL ======== */
function PV({ tag, value, unit, min = 0, max = 100, alarmHi, alarmLo }) {
  const pct = Math.max(0, Math.min(100, ((value - min) * 100) / (max - min)));
  const warn =
    (typeof alarmHi === "number" && value >= alarmHi) ||
    (typeof alarmLo === "number" && value <= alarmLo);

  return (
    <div style={{ ...panelBase, padding: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <div style={{ color: "#9aa4af", fontSize: 12 }}>{tag}</div>
        <div style={{ fontWeight: 700, fontSize: 18 }}>
          {typeof value === "number" ? value.toFixed(1) : value}{" "}
          <span style={{ color: "#9aa4af" }}>{unit}</span>
        </div>
      </div>
      <div
        style={{
          marginTop: 8,
          height: 8,
          borderRadius: 4,
          background: "#23292f",
          overflow: "hidden",
          border: "1px solid #2e343b",
        }}
      >
        <div
          style={{
            width: `${pct}%`,
            height: "100%",
            background: warn ? "#f55" : "#2bd673",
            transition: "width 300ms linear",
          }}
        />
      </div>
    </div>
  );
}

/** ======== TANK SVG (flat DCS style) ======== */
function TankGraphic({ levelPct }) {
  const L = Math.max(0, Math.min(100, levelPct));
  const W = 220, H = 360, x = 40, y = 40;
  const liquidH = (H * L) / 100;

  return (
    <svg width="100%" height="100%" viewBox="0 0 900 560">
      <g stroke="#7aa5ff" strokeWidth="6" fill="none" opacity="0.8">
        <path d="M340 340 H520 V420 H720" />
        <path d="M150 360 H40" />
      </g>

      <rect x={x} y={y} width={W} height={H} rx="12" fill="#0f1113" stroke="#69737e" strokeWidth="4" />
      <rect x={x+2} y={y+H-liquidH} width={W-4} height={liquidH} fill="#1f89ff" opacity="0.85" />

      <g fontSize="10" fill="#9aa4af">
        {[0,25,50,75,100].map(t => (
          <g key={t}>
            <line x1={x+W+6} x2={x+W+18} y1={y+H-(H*t)/100} y2={y+H-(H*t)/100} stroke="#4b545d" />
            <text x={x+W+24} y={y+H-(H*t)/100+4}>{t}%</text>
          </g>
        ))}
      </g>

      <g transform="translate(570,400)">
        <circle r="28" fill="#0f1113" stroke="#69737e" strokeWidth="4" />
        <polygon points="-12,-18 22,0 -12,18" fill="#838f9a" stroke="#69737e" strokeWidth="2" />
        <text x="-16" y="48" fill="#9aa4af" fontSize="12">P-101</text>
      </g>

      <text x={x+60} y={y-10} fill="#9aa4af" fontSize="12">T-101</text>
    </svg>
  );
}

/** ======== MAIN PAGE ======== */
export default function DCSDashboard() {
  const [connOK, setConnOK] = useState(false);
  const [pump, setPump]   = useState(false);

  // PVs
  const [level, setLevel] = useState(35);
  const [flow,  setFlow]  = useState(0);
  const [temp,  setTemp]  = useState(26);
  const [press, setPress] = useState(0);

  // alarms + audio
  const [alarms, setAlarms]         = useState([]);
  const [alarmAck, setAlarmAck]     = useState(false); // user silenced
  const [audioReady, setAudioReady] = useState(false);
  const audioRef = useRef(null);

  // WS handling
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);

  /** ----- WebSocket connect + auto-reconnect ----- */
  useEffect(() => {
    let closed = false;
    let backoff = 500;

    const connect = () => {
      if (closed) return;
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnOK(true);
        backoff = 500;
      };

      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          if (msg.pump === "on") setPump(true);
          if (msg.pump === "off") setPump(false);
        } catch {/* ignore */}
      };

      ws.onclose = () => {
        setConnOK(false);
        if (!closed) {
          clearTimeout(reconnectRef.current);
          reconnectRef.current = setTimeout(connect, backoff);
          backoff = Math.min(backoff * 2, 5000);
        }
      };

      ws.onerror = () => ws.close();
    };

    connect();
    return () => {
      closed = true;
      try { wsRef.current && wsRef.current.close(); } catch {}
      clearTimeout(reconnectRef.current);
    };
  }, []);

  /** ----- Send command to Pi ----- */
  const sendPump = (on) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ command: "pump", state: on ? "on" : "off", gpio: 17 }));
    }
  };

  /** ----- Unlock audio (autoplay policy) ----- */
  const unlockAudio = () => {
    if (audioReady || !audioRef.current) return;
    audioRef.current.play()
      .then(() => { audioRef.current.pause(); audioRef.current.currentTime = 0; setAudioReady(true); })
      .catch(() => { /* will retry on next click */ });
  };

  /** ----- Pump buttons ----- */
  const handleRun  = () => { unlockAudio(); if (!pump) { sendPump(true);  setPump(true);  } };
  const handleStop = () => { unlockAudio(); if (pump)  { sendPump(false); setPump(false); } };

  /** ----- Process simulation ----- */
  useEffect(() => {
    const t = setInterval(() => {
      setFlow(() => (pump ? 55 : 0));
      setPress(p => (pump ? 14.5 : Math.max(0, p - 1)));
      setLevel(l => pump ? Math.min(100, l + 0.20) : Math.max(0, l - 0.08));
      setTemp (t0 => pump ? Math.min(80,  t0 + 0.04) : Math.max(20, t0 - 0.02));

      // simple alarm list
      setAlarms(() => {
        const a = [];
        if (level <= LOW_LEVEL) a.push({ sev: "LOW",  tag: "LT-101", msg: "LOW LEVEL"  });
        if (level >= 95)        a.push({ sev: "HIGH", tag: "LT-101", msg: "HIGH LEVEL" });
        return a;
      });
    }, POLL_MS);
    return () => clearInterval(t);
  }, [pump, level]);

  /** ----- Alarm state + snooze reset ----- */
  const alarmActive  = level <= LOW_LEVEL;
  const alarmCleared = level >= CLEAR_LEVEL;

  // auto-reset ACK when cleared so next occurrence will sound
  useEffect(() => {
    if (alarmCleared && alarmAck) setAlarmAck(false);
  }, [alarmCleared, alarmAck]);

  /** ----- Alarm sound control ----- */
  useEffect(() => {
    const a = audioRef.current;
    if (!a || !audioReady) return;

    if (alarmActive && !alarmAck) {
      a.loop = true;
      a.play().catch(() => {});
    } else {
      if (!a.paused) a.pause();
      a.currentTime = 0;
    }
  }, [alarmActive, alarmAck, audioReady]);

  // pause when tab hidden, resume when visible and still alarming
  useEffect(() => {
    const h = () => {
      const a = audioRef.current;
      if (!a) return;
      if (document.hidden && !a.paused) a.pause();
      else if (!document.hidden && alarmActive && !alarmAck && audioReady) {
        a.play().catch(()=>{});
      }
    };
    document.addEventListener("visibilitychange", h);
    return () => document.removeEventListener("visibilitychange", h);
  }, [alarmActive, alarmAck, audioReady]);

  const datetime = useMemo(() => new Date().toLocaleString(), [connOK, pump]);

  /** ----- RENDER ----- */
  return (
    <div style={appStyle} onClick={unlockAudio}>
      {/* Hidden audio element */}
      <audio ref={audioRef} src="/alarm.wav" preload="auto" />

      {/* Top Bar */}
      <div style={{ ...bar, gridArea: "topbar" }}>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <div style={{ fontWeight: 800, letterSpacing: "1px" }}>
            UNIT 400 — TANK CONTROL
          </div>
          <div style={statusPill(connOK)}>{connOK ? "CONNECTED" : "DISCONNECTED"}</div>
          <div style={statusPill(pump)}>P-101 {pump ? "RUNNING" : "STOPPED"}</div>
        </div>
        <div style={{ color: "#9aa4af", fontSize: 13 }}>{datetime}</div>
      </div>

      {/* Left: Controls */}
      <div style={leftPanel}>
        <div>
          <div style={sectionTitle}>Pump Controls</div>
          <div style={{ display: "grid", gap: 10 }}>
            <button style={btn(pump)} onClick={handleRun} disabled={pump}>
              <span style={lamp(pump, "#2bd673")} />
              RUN P-101
            </button>
            <button style={btn(false, true)} onClick={handleStop} disabled={!pump}>
              <span style={lamp(!pump, "#e04f4f")} />
              STOP P-101
            </button>
          </div>
        </div>

        <div>
          <div style={sectionTitle}>Connection</div>
          <div style={{ ...panelBase, display: "grid", gap: 8, fontSize: 13, color: "#c3cbd4" }}>
            <div>WS URL: <span style={{ color: "#9aa4af" }}>{WS_URL}</span></div>
            <div>Status: <span style={{ color: connOK ? "#7fffb2" : "#ff8e8e" }}>
              {connOK ? "Online" : "Offline"}
            </span></div>
          </div>
        </div>
      </div>

      {/* Main: Process Graphic */}
      <div style={mainPanel}>
        <TankGraphic levelPct={level} />
        <div style={{ position: "absolute", left: 40, top: 12, fontSize: 12, color: "#9aa4af" }}>
          Process Overview
        </div>
      </div>

      {/* Right: Instruments */}
      <div style={rightPanel}>
        <div style={sectionTitle}>Instruments</div>
        <PV tag="LT-101" value={level} unit="%"   min={0} max={100} alarmLo={LOW_LEVEL} alarmHi={95} />
        <PV tag="FT-104" value={flow}  unit="gpm" min={0} max={100} />
        <PV tag="PT-102" value={press} unit="psi" min={0} max={30} />
        <PV tag="TT-103" value={temp}  unit="°C"  min={0} max={100} />
      </div>

      {/* Bottom: Alarms + ACK (snooze) */}
      <div style={alarmBar}>
        <div style={{ color: "#9aa4af", marginRight: 6 }}>ALARMS</div>

        {alarmActive ? (
          <>
            <div style={{
              padding: "4px 10px",
              borderRadius: 12,
              border: "1px solid #ff6969",
              color: "#ff6969",
              background: "rgba(255,105,105,0.12)",
            }}>
              LT-101 LOW LEVEL (≤ {LOW_LEVEL}%)
            </div>

            {!alarmAck ? (
              <button
                onClick={() => { unlockAudio(); setAlarmAck(true); }}
                style={{ marginLeft: 8, padding: "6px 10px", background: "#3a3f45", border: "1px solid #666", color: "#eee", borderRadius: 6, cursor: "pointer" }}
              >
                ACK / SILENCE
              </button>
            ) : (
              <div style={{ marginLeft: 8, color: "#ffc15a" }}>
                Acknowledged (until cleared ≥ {CLEAR_LEVEL}%)
              </div>
            )}
          </>
        ) : (
          <div style={{ color: "#7fffb2" }}>No active alarms</div>
        )}
      </div>
    </div>
  );
}
