import React from "react";
import TerminalLoadingBar from "./TerminalLoadingBar";

const labels = {
  NOT_CONFIGURED: "Not configured",
  CONNECTING: "Connecting",
  CONNECTED: "Connected",
  DEGRADED: "Connected (no data >10s)",
  OFFLINE: "Offline",
  ERROR: "Error",
};

const colors = {
  NOT_CONFIGURED: "#848e9a",
  CONNECTED: "#2d5",
  DEGRADED: "#d9b300",
  OFFLINE: "#e04f4f",
  ERROR: "#e04f4f",
};

export default function ConnBadge({ state, latencyMs }) {
  if (state === "CONNECTING") return <TerminalLoadingBar />;

  const color = colors[state] || "#848e9a";
  const label = labels[state] || state;
  const showLatency = latencyMs != null && state === "CONNECTED";

  return (
    <div
      style={{
        padding: "4px 10px",
        borderRadius: 12,
        border: `1px solid ${color}`,
        color,
        background: "rgba(255,255,255,0.05)",
        fontSize: 13,
      }}
    >
      {label}
      {showLatency && ` ${latencyMs} ms`}
    </div>
  );
}
