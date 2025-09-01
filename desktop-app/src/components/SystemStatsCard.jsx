import React from "react";

function SystemStatsCard({ stats }) {
  const uptime = (s) => {
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = s % 60;
    return `${h}h ${m}m ${sec}s`;
  };

  const pill = () => {
    const state = stats?.service?.active || "inactive";
    const base = "px-2 py-0.5 rounded-full text-xs capitalize";
    if (state === "running") return `${base} bg-green-600 text-white`;
    if (state === "failed") return `${base} bg-red-600 text-white`;
    return `${base} bg-gray-600 text-white`;
  };

  return (
    <div className="bg-[#15181b] border-2 border-[#32373e] rounded p-3 text-xs text-gray-300 font-mono">
      <div className="flex items-center justify-between mb-2">
        <div className="uppercase text-gray-400">System Stats</div>
        {stats && <span className={pill()}>{stats.service.active}</span>}
      </div>
      {stats ? (
        <div className="grid grid-cols-2 gap-y-1">
          <div>CPU</div>
          <div className="text-right">{stats.cpu_pct.toFixed(1)}%</div>
          <div>CPU Temp</div>
          <div className="text-right">
            {stats.cpu_temp_c !== null ? `${stats.cpu_temp_c.toFixed(1)}°C` : "n/a"}
          </div>
          <div>Memory</div>
          <div className="text-right">{stats.mem_pct.toFixed(1)}%</div>
          <div>Disk /</div>
          <div className="text-right">{stats.disk_root_pct.toFixed(1)}%</div>
          <div>Uptime</div>
          <div className="text-right">{uptime(stats.uptime_s)}</div>
        </div>
      ) : (
        <div className="text-gray-500">No data</div>
      )}
    </div>
  );
}

export default SystemStatsCard;
