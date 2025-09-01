// Minimal reconnecting WebSocket with backoff + jitter.
// Internal helper; do not export to UI.
export function spawnAutoWS(url, handlers = {}, opts = {}) {
  const { onOpen, onMessage, onClose, onError } = handlers;
  const {
    initialDelay = 500,
    maxDelay = 8000,
    jitterRatio = 0.1,
    onPlannedRetry,
  } = opts;

  let ws = null;
  let stopped = false;
  let delay = initialDelay;
  let timer = null;

  const jitter = (ms) => {
    const j = ms * jitterRatio;
    return ms + (Math.random() * 2 * j - j); // ±10%
  };

  const connect = () => {
    if (stopped) return;
    try {
      ws = new WebSocket(url);
    } catch (e) {
      onError?.(e);
      scheduleReconnect();
      return;
    }

    ws.onopen = (ev) => {
      delay = initialDelay;
      onOpen?.(ev);
    };

    ws.onmessage = (ev) => onMessage?.(ev);

    ws.onclose = (ev) => {
      onClose?.(ev);
      scheduleReconnect();
    };

    ws.onerror = (ev) => {
      onError?.(ev);
      try { ws.close(); } catch {}
    };
  };

  const scheduleReconnect = () => {
    if (stopped) return;
    const wait = Math.round(jitter(delay));
    timer = setTimeout(connect, wait);
    delay = Math.min(delay * 2, maxDelay);
    onPlannedRetry?.(wait);
  };

  const start = () => { connect(); };
  const stop = () => {
    stopped = true;
    if (timer) clearTimeout(timer);
    try { ws && ws.close(); } catch {}
  };
  const poke = () => {
    if (timer) clearTimeout(timer);
    delay = initialDelay;
    try { ws && ws.close(); } catch {}
    timer = setTimeout(connect, 0);
  };
  const send = (data) => {
    try {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(data);
        return true;
      }
    } catch {}
    return false;
  };

  return { start, stop, poke, send };
}
