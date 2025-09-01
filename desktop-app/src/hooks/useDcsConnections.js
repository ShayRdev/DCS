import { useEffect, useRef, useState } from "react";
import { spawnAutoWS } from "../utils/autoWS";

const HOST = process.env.REACT_APP_PI_HOST || window.location.hostname;
const RELAY_WS = `ws://${HOST}:${process.env.REACT_APP_RELAY_PORT || 8765}`;
const STATS_WS = `ws://${HOST}:${process.env.REACT_APP_STATS_PORT || 8770}`;

export function useDcsConnections({ onRelayMessage, onStatsMessage } = {}) {
  const [relayConnected, setRelayConnected] = useState(false);
  const [statsConnected, setStatsConnected] = useState(false);
  const [connecting, setConnecting] = useState(true);
  const [retryInMs, setRetryInMs] = useState(0);
  const [statusText, setStatusText] = useState("connecting…");
  const [lastError, setLastError] = useState(null);

  const relayRef = useRef(null);
  const statsRef = useRef(null);

  const updateStatus = () => {
    const both = relayConnected && statsConnected;
    if (both) {
      setConnecting(false);
      setStatusText("connected");
      setRetryInMs(0);
    } else if (retryInMs > 0) {
      setConnecting(true);
      setStatusText(`waiting ${(retryInMs / 1000).toFixed(1)}s to retry…`);
    } else {
      setConnecting(true);
      setStatusText("connecting…");
    }
  };

  useEffect(updateStatus, [relayConnected, statsConnected, retryInMs]);

  // countdown for retryInMs
  useEffect(() => {
    if (retryInMs > 0) {
      const t = setInterval(() => {
        setRetryInMs((ms) => (ms > 200 ? ms - 200 : 0));
      }, 200);
      return () => clearInterval(t);
    }
  }, [retryInMs]);

  useEffect(() => {
    const updateRetry = (ms) => {
      setRetryInMs((prev) => (prev === 0 ? ms : Math.min(prev, ms)));
    };

    relayRef.current = spawnAutoWS(
      RELAY_WS,
      {
        onOpen: () => setRelayConnected(true),
        onClose: () => setRelayConnected(false),
        onError: (e) => setLastError((e && e.message) || "relay error"),
        onMessage: (e) => onRelayMessage?.(e.data),
      },
      { onPlannedRetry: updateRetry }
    );

    statsRef.current = spawnAutoWS(
      STATS_WS,
      {
        onOpen: () => setStatsConnected(true),
        onClose: () => setStatsConnected(false),
        onError: (e) => setLastError((e && e.message) || "stats error"),
        onMessage: (e) => onStatsMessage?.(e.data),
      },
      { onPlannedRetry: updateRetry }
    );

    relayRef.current.start();
    statsRef.current.start();

    const vis = () => {
      if (
        document.visibilityState === "visible" &&
        !(relayConnected && statsConnected)
      ) {
        relayRef.current?.poke();
        statsRef.current?.poke();
      }
    };
    document.addEventListener("visibilitychange", vis);

    return () => {
      document.removeEventListener("visibilitychange", vis);
      relayRef.current?.stop();
      statsRef.current?.stop();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const connectNow = () => {
    setStatusText("connecting…");
    setRetryInMs(0);
    relayRef.current?.poke();
    statsRef.current?.poke();
  };

  const sendRelay = (data) => relayRef.current?.send(data);

  return {
    connected: relayConnected && statsConnected,
    relayConnected,
    statsConnected,
    connecting,
    retryInMs,
    statusText,
    lastError,
    connectNow,
    sendRelay,
  };
}
