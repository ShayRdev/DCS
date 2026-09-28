# DCS SKiDL project

Generates a KiCad netlist and (optionally) an editable `.kicad_sch` from
[`docs/hardware/CONNECTIONS.md`](../../docs/hardware/CONNECTIONS.md) (sole electrical source of truth).

## Layout

| File | Role |
|------|------|
| `main.py` | Build circuit (SKIDL templates), `ERC()`, write `.net` / BOM / checklist |
| `schematic.py` | **Same nets**, KiCad **stock symbols**, `generate_schematic()` → `.kicad_sch` |
| `stock_parts.py` | Load `Device` / `Analog_ADC` / `Connector_Generic` / `power` from `KICAD*_SYMBOL_DIR` |
| `parts.py` | Offline SKIDL part templates (stock mirrors + connector stand-ins) |
| `power.py` | PS1 Mean Well, rails, `PWR_FLAG`, J2–J4 |
| `loop.py` | J1 Rosemount + R1 250 Ω shunt |
| `mcu.py` | U1 Pi (Conn_01x06 stand-in **or** Conn_02x20_Odd_Even) |
| `level_shifter.py` | U3 blue 4-ch LLC |
| `adc.py` | U2 ADS1115 + **optional** AIN0 clamp |
| `designators.py` | CONNECTIONS.md ↔ schematic refs |
| `out/` | Generated netlist, BOM, ERC log, checklist, `.kicad_sch` |
| `STANDINS.md` | Which symbols are generic stand-ins |

## Designators

| Ref | CONNECTIONS.md | Part |
|-----|----------------|------|
| U1 | U_PI | Raspberry Pi 4 (`Conn_02x20_Odd_Even` in schematic.py; Conn_01x06 in main.py) |
| U2 | U_ADS | ADS1115 (`Analog_ADC:ADS1115IDGS`) |
| U3 | U_LLC | 4 Bi-Directional Level Shifters (`Conn_01x12`) |
| R1 | RS250 | 250 Ω shunt (`Device:R`) |
| PS1 | PSU_MW | Mean Well DIN 24 V (`Conn_01x04` — silk TODO) |
| J1 | TT_RM | Rosemount terminals |

`0V_LOOP` is **merged into `GND`**.

## Run — netlist / BOM (no KiCad libs required)

```bash
cd hardware/skidl
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
python3 main.py
```

Outputs: `out/dcs.net`, `out/bom.csv`, `out/kicad-verify-checklist.md`, `out/erc.log`

## Run — KiCad schematic (`.kicad_sch`)

Needs **KiCad symbol libraries on disk**. There is no pip “schematic extra” beyond
`skidl` + `simp_sexp` (listed in `requirements.txt`); `generate_schematic()` is
built into SKiDL 2.x. The blocker is the env var pointing at `*.kicad_sym`.

```bash
cd hardware/skidl
pip install -r requirements.txt

# ——— pick ONE env var matching your KiCad major version ———

# macOS (KiCad 8 app bundle — most common for this bench):
export KICAD8_SYMBOL_DIR=/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols

# macOS KiCad 9:
# export KICAD9_SYMBOL_DIR=/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols

# Linux (distro packages):
# export KICAD8_SYMBOL_DIR=/usr/share/kicad/symbols
# export KICAD9_SYMBOL_DIR=/usr/share/kicad/symbols

# Windows (PowerShell example):
# $env:KICAD8_SYMBOL_DIR="C:\Program Files\KiCad\8.0\share\kicad\symbols"

python3 schematic.py
```

`schematic.py` also auto-detects those common paths if the env var is unset.

Outputs:

- `out/dcs.kicad_sch` — open in KiCad Schematic Editor
- `out/schematic-notes.md` — command, env, ERC / generate outcome
- `out/schematic.log` — transcript

If symbol libs are missing, the script **exits non-zero** and writes failure notes
(no empty / fake `.kicad_sch`).

### Stock symbols used by `schematic.py`

| Ref | Symbol |
|-----|--------|
| R1, R2 | `Device:R` |
| D1, D2 | `Device:D` |
| U2 | `Analog_ADC:ADS1115IDGS` |
| U1 | `Connector_Generic:Conn_02x20_Odd_Even` |
| U3 | `Connector_Generic:Conn_01x12` |
| PS1 | `Connector_Generic:Conn_01x04` (stand-in) |
| J1–J4 | `Connector_Generic:Conn_01x02` |
| flags | `power:PWR_FLAG` |

## Optional AIN0 protection

`R2` (1k) + `D1`/`D2` (1N4148 clamps to `+5V_ADS` / `GND`) protect against Rosemount **alarm** current ≈23 mA → **5.75 V** on a 250 Ω shunt into a 5 V ADS1115. Toggle with `INCLUDE_OPTIONAL_AIN0_PROTECTION` in `main.py` / `schematic.py`.

## Non-goals

- WebSocket / desktop app are software-only.
- No Serial Dynamics branding.
- Unused LLC / AIN pins left NC (CONNECTIONS TODOs not invented).
