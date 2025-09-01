import React, { useEffect } from 'react';
import LogViewer from './LogViewer';

export default function PumpLogsModal({
  isOpen,
  onClose,
  logs,
  onClear,
  paused,
  onPauseToggle,
  serviceActive,
}) {
  // close on escape
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const pillColor =
    serviceActive === 'active'
      ? 'bg-green-500/20 text-green-400'
      : 'bg-red-500/20 text-red-400';

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-gray-900 text-teal-300 w-full max-w-3xl rounded shadow-lg flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <span>Unit 400 &rsaquo; P-101 &rsaquo; Logs</span>
            {serviceActive && (
              <span className={`text-xs px-2 py-0.5 rounded ${pillColor}`}>
                Service {serviceActive}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 text-xs">
            <button
              onClick={onPauseToggle}
              className="bg-gray-800 px-2 py-0.5 rounded"
            >
              {paused ? 'Resume' : 'Pause'}
            </button>
            <button onClick={onClear} className="bg-gray-800 px-2 py-0.5 rounded">
              Clear
            </button>
          </div>
        </div>
        <div className="p-4 flex-1 overflow-hidden">
          <LogViewer lines={logs} paused={paused} />
        </div>
        <div className="p-3 border-t border-gray-700 text-right">
          <button onClick={onClose} className="bg-gray-800 px-3 py-1 rounded text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
