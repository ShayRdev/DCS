import React, { useEffect, useRef, useState } from 'react';

/**
 * Generic log viewer with optional filtering and controls.
 *
 * Props:
 *  - lines: string[]            Lines of text to display
 *  - onClear?: () => void       Called when Clear is pressed
 *  - onPauseToggle?: () => void Called when Pause/Resume is pressed
 *  - paused?: boolean           When true, auto-scroll is disabled
 *  - header?: string            Optional title to show in the header
 */
export default function LogViewer({
  lines,
  onClear,
  onPauseToggle,
  paused = false,
  header,
}) {
  const [filter, setFilter] = useState('');
  const bottomRef = useRef(null);

  // auto-scroll to bottom when new lines arrive and not paused
  useEffect(() => {
    if (!paused) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [lines, paused, filter]);

  const filtered = lines.filter((l) =>
    l.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="bg-gray-900 text-teal-300 p-4 rounded shadow font-mono text-xs flex flex-col h-64">
      <div className="flex items-center mb-2 space-x-2">
        {header && <span className="font-bold">{header}</span>}
        <input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="flex-1 bg-gray-800 text-teal-300 px-1 py-0.5 text-xs rounded"
          placeholder="filter"
        />
        {onPauseToggle && (
          <button
            onClick={onPauseToggle}
            className="bg-gray-800 px-2 py-0.5 rounded"
          >
            {paused ? 'Resume' : 'Pause'}
          </button>
        )}
        {onClear && (
          <button onClick={onClear} className="bg-gray-800 px-2 py-0.5 rounded">
            Clear
          </button>
        )}
      </div>
      <pre className="flex-1 overflow-y-auto whitespace-pre-wrap">
        {filtered.map((line, i) => (
          <div key={i}>{line}</div>
        ))}
        <div ref={bottomRef} />
      </pre>
    </div>
  );
}
