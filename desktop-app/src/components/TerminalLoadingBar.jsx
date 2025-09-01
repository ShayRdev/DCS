import React, { useEffect, useState } from "react";

const frames = [
  "[>         ]",
  "[=>        ]",
  "[==>       ]",
  "[===>      ]",
  "[====>     ]",
  "[=====>    ]",
  "[======>   ]",
  "[=======>  ]",
  "[========> ]",
  "[=========>]",
];

export default function TerminalLoadingBar() {
  const [i, setI] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setI((v) => (v + 1) % frames.length), 150);
    return () => clearInterval(t);
  }, []);

  return (
    <span
      role="status"
      aria-live="polite"
      style={{ fontFamily: "monospace", whiteSpace: "pre" }}
    >
      <span style={{ display: "inline-block", width: "14ch" }}>{frames[i]}</span>
      connecting…
    </span>
  );
}
