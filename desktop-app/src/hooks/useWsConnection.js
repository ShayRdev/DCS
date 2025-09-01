import { useCallback, useEffect, useRef, useState } from "react";

const BACKOFF_STEPS = [1000, 2000, 4000, 8000, 16000, 30000];

export function useWsConnection(url, onMessage) {
  const [state, setState] = useState(url ? "CONNECTING" : "NOT_CONFIGURED");
  const [readyState, setReadyState] = useState(WebSocket.CLOSED);
  const [latencyMs, setLatencyMs] = useState(null);
  const [lastMsgAt, setLastMsgAt] = useState(null);

  const wsRef = useRef(null);
  const hbRef = useRef(null);
  const healthRef = useRef(null);
  const reconnectRef = useRef(null);
  const backoffRef = useRef(0);
  const lastMsgRef = useRef(null);

  const clearTimers = () => {
    clearInterval(hbRef.current); hbRef.current = null;
    clearInterval(healthRef.current); healthRef.current = null;
    clearTimeout(reconnectRef.current); reconnectRef.current = null;
  };

  function scheduleReconnect() {
    if (!url) return;
    const delay = BACKOFF_STEPS[Math.min(backoffRef.current, BACKOFF_STEPS.length - 1)];
    reconnectRef.current = setTimeout(() => {
      backoffRef.current = Math.min(backoffRef.current + 1, BACKOFF_STEPS.length - 1);
      doConnect();
    }, delay);
  }

  function doConnect() {
    if (!url) {
      setState("NOT_CONFIGURED");
      return;
    }

    clearTimers();
    if (wsRef.current) {
      try { wsRef.current.close(); } catch {}
    }

    setState("CONNECTING");
    setReadyState(WebSocket.CONNECTING);

    const ws = new WebSocket(url);
    wsRef.current = ws;
    lastMsgRef.current = Date.now();
    setLastMsgAt(lastMsgRef.current);

    ws.onopen = () => {
      setState("CONNECTED");
      setReadyState(ws.readyState);
      backoffRef.current = 0;
      clearInterval(hbRef.current);
      hbRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          try { ws.send(JSON.stringify({ type: "ping", t: Date.now() })); } catch {}
        }
      }, 5000);
    };

    ws.onmessage = (ev) => {
      lastMsgRef.current = Date.now();
      setLastMsgAt(lastMsgRef.current);
      let msg;
      try { msg = JSON.parse(ev.data); } catch { msg = ev.data; }
      if (msg && msg.type === "pong" && typeof msg.t === "number") {
        setLatencyMs(Date.now() - msg.t);
      } else if (msg !== undefined) {
        onMessage && onMessage(msg);
      }
    };

    ws.onclose = () => {
      setReadyState(ws.readyState);
      clearInterval(hbRef.current);
      setState("OFFLINE");
      scheduleReconnect();
    };

    ws.onerror = () => {
      setReadyState(ws.readyState);
      clearInterval(hbRef.current);
      setState("ERROR");
      try { ws.close(); } catch {}
      scheduleReconnect();
    };

    clearInterval(healthRef.current);
    healthRef.current = setInterval(() => {
      const w = wsRef.current;
      const rs = w ? w.readyState : WebSocket.CLOSED;
      setReadyState(rs);
      if (w && rs === WebSocket.OPEN) {
        const diff = Date.now() - (lastMsgRef.current || 0);
        if (diff > 10000) {
          setState((s) => (s !== "DEGRADED" ? "DEGRADED" : s));
        } else {
          setState((s) => (s === "DEGRADED" ? "CONNECTED" : s));
        }
      } else {
        setState((s) => {
          if (s === "CONNECTING" || s === "NOT_CONFIGURED" || s === "ERROR") return s;
          return "OFFLINE";
        });
      }
    }, 1000);
  }

  const connect = useCallback(() => {
    backoffRef.current = 0;
    clearTimeout(reconnectRef.current);
    doConnect();
  }, [url]);

  useEffect(() => {
    if (url) {
      connect();
    } else {
      setState("NOT_CONFIGURED");
    }
    return () => {
      clearTimers();
      if (wsRef.current) {
        try { wsRef.current.close(); } catch {}
        wsRef.current = null;
      }
    };
  }, [url, connect]);

  const send = useCallback((obj) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(obj));
      return true;
    }
    return false;
  }, []);

  return { state, readyState, latencyMs, lastMsgAt, connect, send };
}
