import React, { useEffect, useRef, useState } from "react";

function LogViewer({ lines = [], onClear }) {
  const [filter, setFilter] = useState("");
  const [paused, setPaused] = useState(false);
  const boxRef = useRef(null);

  useEffect(() => {
    if (!paused && boxRef.current) {
      boxRef.current.scrollTop = boxRef.current.scrollHeight;
    }
  }, [lines, paused]);

  const handleClear = () => {
    if (onClear) onClear();
  };

  const filtered = lines.filter((l) =>
    l.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="bg-[#15181b] border-2 border-[#32373e] rounded p-3 text-xs text-gray-300 font-mono flex flex-col h-64">
      <div className="flex items-center justify-between mb-2">
        <div className="uppercase text-gray-400">Logs</div>
        <div className="flex items-center gap-2">
          <input
            className="bg-[#0f1113] border border-[#32373e] rounded px-1 py-0.5 text-xs"
            placeholder="filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          <button
            className="border border-[#32373e] rounded px-2 py-0.5"
            onClick={() => setPaused((p) => !p)}
          >
            {paused ? "Resume" : "Pause"}
          </button>
          <button
            className="border border-[#32373e] rounded px-2 py-0.5"
            onClick={handleClear}
          >
            Clear
          </button>
        </div>
      </div>
      <pre ref={boxRef} className="flex-1 overflow-y-auto bg-[#0f1113] p-2 rounded">
        {filtered.join("\n")}
      </pre>
    </div>
  );
}

export default LogViewer;
