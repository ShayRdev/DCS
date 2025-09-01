import React from 'react';

function fmtUptime(s) {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  return `${h}h ${m}m ${sec}s`;
}

export default function SystemStatsCard({ stats }) {
  if (!stats) return null;
  const status = stats.service?.active || 'inactive';
  const pillColor =
    status === 'running'
      ? 'bg-green-600'
      : status === 'failed'
      ? 'bg-red-600'
      : 'bg-gray-600';
  return (
    <div className="bg-gray-900 text-teal-300 p-4 rounded shadow font-mono text-xs">
      <div className="flex items-center justify-between mb-2">
        <span className="font-bold">SYSTEM</span>
        <span className={`px-2 py-0.5 rounded-full text-[10px] text-white ${pillColor}`}>
          {status}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-x-2 gap-y-1">
        <span>CPU</span>
        <span className="text-right">{stats.cpu_pct.toFixed(1)}%</span>
        <span>CPU Temp</span>
        <span className="text-right">
          {stats.cpu_temp_c != null ? stats.cpu_temp_c.toFixed(1) : 'N/A'}°C
        </span>
        <span>Memory</span>
        <span className="text-right">{stats.mem_pct.toFixed(1)}%</span>
        <span>Disk /</span>
        <span className="text-right">{stats.disk_root_pct.toFixed(1)}%</span>
        <span>Uptime</span>
        <span className="text-right">{fmtUptime(stats.uptime_s)}</span>
      </div>
    </div>
  );
}
