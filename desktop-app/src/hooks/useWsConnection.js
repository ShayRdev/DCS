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
  const missedBeatsRef = useRef(0);
  const firstMsgRef = useRef(false);
  const lastMsgRef = useRef(null);
  const onMsgRef = useRef(onMessage);
  const msgQueueRef = useRef([]);
  const rafRef = useRef(null);

  useEffect(() => {
    onMsgRef.current = onMessage;
  }, [onMessage]);

  const clearTimers = () => {
    clearInterval(hbRef.current); hbRef.current = null;
    clearInterval(healthRef.current); healthRef.current = null;
    clearTimeout(reconnectRef.current); reconnectRef.current = null;
    if (rafRef.current) cancelAnimationFrame(rafRef.current); rafRef.current = null;
  };

  const scheduleReconnect = () => {
    if (!url) return;
    const base = BACKOFF_STEPS[Math.min(backoffRef.current, BACKOFF_STEPS.length - 1)];
    const jitter = base * (Math.random() * 0.4 - 0.2);
    reconnectRef.current = setTimeout(() => {
      backoffRef.current = Math.min(backoffRef.current + 1, BACKOFF_STEPS.length - 1);
      doConnect();
    }, base + jitter);
  };

  const flushQueue = () => {
    rafRef.current = null;
    const queue = msgQueueRef.current;
    msgQueueRef.current = [];
    queue.forEach((msg) => {
      if (msg && msg.type === "pong" && typeof msg.t === "number") {
        setLatencyMs(Date.now() - msg.t);
      } else if (msg !== undefined) {
        onMsgRef.current && onMsgRef.current(msg);
      }
    });
  };

  const doConnect = () => {
    if (!url) {
      setState("NOT_CONFIGURED");
      return;
    }

    const existing = wsRef.current;
    if (existing && (existing.readyState === WebSocket.OPEN || existing.readyState === WebSocket.CONNECTING)) {
      return; // already connected or connecting
    }

    clearTimers();
    setState("CONNECTING");
    setReadyState(WebSocket.CONNECTING);

    const ws = new WebSocket(url);
    wsRef.current = ws;
    firstMsgRef.current = false;
    missedBeatsRef.current = 0;
    lastMsgRef.current = Date.now();
    setLastMsgAt(lastMsgRef.current);

    ws.onopen = () => {
      setReadyState(ws.readyState);
      hbRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          try { ws.send(JSON.stringify({ type: "ping", t: Date.now() })); } catch {}
        }
      }, 5000);
    };

    ws.onmessage = (ev) => {
      lastMsgRef.current = Date.now();
      setLastMsgAt(lastMsgRef.current);
      missedBeatsRef.current = 0;
      if (!firstMsgRef.current) {
        backoffRef.current = 0;
        firstMsgRef.current = true;
        setState("CONNECTED");
      }
      let msg;
      try { msg = JSON.parse(ev.data); } catch { msg = ev.data; }
      msgQueueRef.current.push(msg);
      if (!rafRef.current) {
        rafRef.current = requestAnimationFrame(flushQueue);
      }
    };

    ws.onclose = () => {
      setReadyState(ws.readyState);
      setState("OFFLINE");
      scheduleReconnect();
    };

    ws.onerror = () => {
      setReadyState(ws.readyState);
      setState("ERROR");
      try { ws.close(); } catch {}
      scheduleReconnect();
    };

    healthRef.current = setInterval(() => {
      const w = wsRef.current;
      const rs = w ? w.readyState : WebSocket.CLOSED;
      setReadyState(rs);
      if (w && rs === WebSocket.OPEN) {
        const diff = Date.now() - (lastMsgRef.current || 0);
        if (diff > 10000) {
          const beats = Math.floor(diff / 10000);
          missedBeatsRef.current = beats;
          if (beats >= 2) {
            setState("OFFLINE");
            try { w.close(); } catch {}
          } else {
            setState("DEGRADED");
          }
        } else {
          missedBeatsRef.current = 0;
          setState((s) => (s === "DEGRADED" ? "CONNECTED" : s));
        }
      } else {
        setState((s) => (
          s === "CONNECTING" || s === "NOT_CONFIGURED" || s === "ERROR" ? s : "OFFLINE"
        ));
      }
    }, 1000);
  };

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

