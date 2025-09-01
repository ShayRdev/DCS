export function autoWS(url, { onOpen, onMessage, onClose, onError } = {}) {
  let ws;
  let backoff = 500; // ms
  const max = 8000;
  let stopped = false;

  const connect = () => {
    if (stopped) return;
    ws = new WebSocket(url);

    ws.onopen = (ev) => {
      backoff = 500;
      onOpen?.(ev);
    };

    ws.onmessage = (ev) => onMessage?.(ev);

    ws.onclose = (ev) => {
      onClose?.(ev);
      if (stopped) return;
      setTimeout(connect, backoff);
      backoff = Math.min(backoff * 2, max);
    };

    ws.onerror = (ev) => {
      onError?.(ev);
      try { ws.close(); } catch {}
    };
  };

  connect();

  return () => {
    stopped = true;
    try { ws && ws.close(); } catch {}
  };
}
