# DCS project historian

Short log of what mattered on this repo. Personal portfolio build — no company branding.

## What the bench is

- **Raspberry Pi 4** reads a **Rosemount-style 2-wire 4–20 mA** temperature transmitter through a **250 Ω** shunt into an **ADS1115** powered at **5 V**.
- I²C crosses a blue **4 Bi-Directional Level Shifters** module on a green perfboard HAT / GPIO screw TB.
- Mean Well **DIN 24 V** supplies the loop; **F1** is a **PT 4-HESI (5×20)** DIN fuse TB in series on the +24 feed before the transmitter (fuse **amp rating** still TBD).
- Pi service prints `V` / `I` / `%Span` and serves **WebSocket `:8765`** to the Electron desktop app. Fluke 789 used for checkout only.

## Timeline of decisions

| When | What |
|------|------|
| Early | Portfolio DCS: Pi + ADS1115 + Electron HMI; simulator for laptop demos |
| Docs pass | PDF pinout/overview sheets; Amazon BOM; README screenshots; WS reconnect polish |
| Hardware truth | Shunt confirmed **250 Ω** (not 100 Ω) from terminal math; ADS @ 5 V + LLC |
| Wire SoT | **`docs/hardware/CONNECTIONS.md`** written as Markdown netlist (rails, From/To, pin tables, TODOs) |
| Schematic attempt | SKiDL / KiCad auto-layout tried for `.net` / `.kicad_sch` — **abandoned** (placement unusable for portfolio display) |
| Schematic SoT | Hand-drawn **SCH-DCS-003** SVG/PDF (`schematic-blocks.*`) kept instead; rev through **H** |
| Fuse | **F1** promoted from vague optional BOM line to confirmed series fuse in CONNECTIONS + drawing |
| Cleanup | **Removed** `hardware/skidl/` and all KiCad/SKiDL tooling from the repo |

## Source of truth (electrical)

1. **`docs/hardware/CONNECTIONS.md`** — wire-level nets and confirmed pins (do not invent TODOs).
2. **`docs/hardware/schematic-blocks.svg` / `.pdf`** — human-readable schematic for the portfolio.
3. Running code under `raspberry-pi/`, `desktop-app/`, `simulator/` for behavior — not for inventing hardware.

## Explicit non-goals / abandoned

- KiCad / SKiDL project, auto-routed `.kicad_sch`, machine BOM-from-SKiDL.
- Drawing WebSocket / Electron as electrical nets.
- Inventing fuse amp rating, Mean Well silk labels, unused AIN/LLC GND ties, or unverified relay hardware.
