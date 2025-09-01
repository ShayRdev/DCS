import React, { useEffect, useState } from "react";

const frames = [
  "[          ]",
  "[==        ]",
  "[====      ]",
  "[======    ]",
  "[========  ]",
  "[==========]",
];

export default function TerminalLoadingBar() {
  const [i, setI] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setI((v) => (v + 1) % frames.length), 250);
    return () => clearInterval(t);
  }, []);
  return (
    <span style={{ fontFamily: "Roboto Mono, Menlo, monospace" }}>
      {frames[i]} connecting…
    </span>
  );
}
