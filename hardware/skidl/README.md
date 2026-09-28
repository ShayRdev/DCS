# DCS SKiDL project

Generates a KiCad netlist from [`docs/hardware/CONNECTIONS.md`](../../docs/hardware/CONNECTIONS.md) (sole electrical source of truth).

## Layout

| File | Role |
|------|------|
| `main.py` | Build circuit, `ERC()`, write `.net` / BOM / checklist |
| `parts.py` | Shared part templates (stock mirrors + connector stand-ins) |
| `power.py` | PS1 Mean Well, rails, `PWR_FLAG`, J2–J4 |
| `loop.py` | J1 Rosemount + R1 250 Ω shunt |
| `mcu.py` | U1 Pi GPIO subset |
| `level_shifter.py` | U3 blue 4-ch LLC |
| `adc.py` | U2 ADS1115 + **optional** AIN0 clamp |
| `designators.py` | CONNECTIONS.md ↔ schematic refs |
| `out/` | Generated netlist, BOM, ERC log, checklist |
| `STANDINS.md` | Which symbols are generic stand-ins |

## Designators

| Ref | CONNECTIONS.md | Part |
|-----|----------------|------|
| U1 | U_PI | Raspberry Pi 4 (Conn stand-in) |
| U2 | U_ADS | ADS1115 |
| U3 | U_LLC | 4 Bi-Directional Level Shifters (Conn stand-in) |
| R1 | RS250 | 250 Ω shunt |
| PS1 | PSU_MW | Mean Well DIN 24 V (Conn stand-in) |
| J1 | TT_RM | Rosemount terminals |

`0V_LOOP` is **merged into `GND`**.

## Run

```bash
cd hardware/skidl
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
python3 main.py
```

Outputs:

- `out/dcs.net` — KiCad netlist
- `out/bom.csv` — BOM
- `out/kicad-verify-checklist.md` — manual checks
- `out/erc.log` — ERC transcript

## KiCad symbol / footprint environment

This generator defines parts with SKiDL templates that **mirror** stock KiCad symbols (see `STANDINS.md`). On a machine with KiCad installed you can optionally point at stock libs:

**Linux (typical):**

```bash
# KiCad 8
export KICAD8_SYMBOL_DIR=/usr/share/kicad/symbols
# KiCad 9
export KICAD9_SYMBOL_DIR=/usr/share/kicad/symbols
# Older
export KICAD6_SYMBOL_DIR=/usr/share/kicad/symbols
```

**macOS:** often under `/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols`  
**Windows:** under `C:\Program Files\KiCad\<version>\share\kicad\symbols`

Footprints (when assigning in PCB): set `KICAD*_FOOTPRINT_DIR` similarly, or configure the footprint library table in KiCad.

Import `out/dcs.net` via KiCad Schematic Editor → File → Import → Netlist (or PCB Editor netlist load, depending on version). Prefer re-annotating after replacing stand-in symbols.

## Optional AIN0 protection

`R2` (1k) + `D1`/`D2` (1N4148 clamps to `+5V_ADS` / `GND`) protect against Rosemount **alarm** current ≈23 mA → **5.75 V** on a 250 Ω shunt into a 5 V ADS1115. Toggle with `INCLUDE_OPTIONAL_AIN0_PROTECTION` in `main.py`.

## Non-goals

- WebSocket / desktop app are software-only.
- No Serial Dynamics branding.
- Unused LLC / AIN pins left NC (CONNECTIONS TODOs not invented).
