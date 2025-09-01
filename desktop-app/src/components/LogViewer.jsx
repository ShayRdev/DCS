import React, { useEffect, useRef, useState } from 'react';

export default function LogViewer({ lines }) {
  const [filter, setFilter] = useState('');
  const [paused, setPaused] = useState(false);
  const [display, setDisplay] = useState([]);
  const [clearedAt, setClearedAt] = useState(0);
  const bottomRef = useRef(null);

  useEffect(() => {
    if (!paused) {
      setDisplay(lines.slice(clearedAt));
    }
  }, [lines, paused, clearedAt]);

  useEffect(() => {
    if (!paused) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [display, paused]);

  const onClear = () => {
    setClearedAt(lines.length);
    setDisplay([]);
  };

  const filtered = display.filter((l) =>
    l.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="bg-gray-900 text-teal-300 p-4 rounded shadow font-mono text-xs flex flex-col h-64">
      <div className="flex items-center mb-2 space-x-2">
        <span className="font-bold">LOGS</span>
        <input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="flex-1 bg-gray-800 text-teal-300 px-1 py-0.5 text-xs rounded"
          placeholder="filter"
        />
        <button
          onClick={() => setPaused((p) => !p)}
          className="bg-gray-800 px-2 py-0.5 rounded"
        >
          {paused ? 'Resume' : 'Pause'}
        </button>
        <button onClick={onClear} className="bg-gray-800 px-2 py-0.5 rounded">
          Clear
        </button>
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
