# SKiDL schematic generation notes

Status: **OK**

## Command (local, with KiCad installed)

```bash
cd hardware/skidl
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# macOS (KiCad 8 — adjust major version to match your install):
export KICAD8_SYMBOL_DIR=/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols

# Linux:
# export KICAD8_SYMBOL_DIR=/usr/share/kicad/symbols

# KiCad 9 / 10: use KICAD9_SYMBOL_DIR or KICAD10_SYMBOL_DIR with the same path.

python3 schematic.py
```

Open: `out/dcs.kicad_sch` in KiCad Schematic Editor.

## Symbol dir used this run

`/tmp/kicad-symbols`

## Designators

| Schematic | CONNECTIONS.md |
|-----------|----------------|
| U1 | U_PI (Conn_02x20_Odd_Even — full 40-pin header) |
| U2 | U_ADS (Analog_ADC:ADS1115IDGS) |
| U3 | U_LLC (Conn_01x12) |
| R1 | RS250 (Device:R) |
| PS1 | PSU_MW (Conn_01x04 stand-in — Mean Well silk TODO) |
| J1–J4 | terminals (Conn_01x02) |
| R2/D1/D2 | OPTIONAL AIN0 clamp |

## Stock symbols used

- `Device:R`, `Device:D`
- `Analog_ADC:ADS1115IDGS`
- `Connector_Generic:Conn_02x20_Odd_Even` (U1 Pi)
- `Connector_Generic:Conn_01x12` (U3 LLC)
- `Connector_Generic:Conn_01x02` / `Conn_01x04` (J*, PS1)
- `power:PWR_FLAG`

## ERC / generate_schematic

```
ERC INFO: No errors or warnings found while running ERC.
(Empty stdout capture; SKiDL 2.x may log via logging module.)

[auto_stub] power: +3V3_PI(3), GND(12), +5V_ADS(5), +24V_LOOP(4) @ [/workspace/hardware/skidl/schematic.py:326=>/workspace/hardware/skidl/schematic.py:255]
  [auto_stub] deferred fanout>=5: __NOCONNECT(43) @ [/workspace/hardware/skidl/schematic.py:326=>/workspace/hardware/skidl/schematic.py:255]
  [selective_routing] Stubbed 1 complex/distant nets after placement @ [/workspace/hardware/skidl/schematic.py:326=>/workspace/hardware/skidl/schematic.py:255]
Schematic written to /workspace/hardware/skidl/out/dcs.kicad_sch @ [/workspace/hardware/skidl/schematic.py:326=>/workspace/hardware/skidl/schematic.py:255]
5 warnings found while generating schematic.
0 errors found while generating schematic.
```

## Output

`/workspace/hardware/skidl/out/dcs.kicad_sch`

## Still verify in KiCad

1. Auto-placement/routing from SKiDL is a starting point — tidy wires and hierarchy.
2. PS1 Mean Well terminal silk (L/N/+V/−V) is TODO — replace Conn_01x04 when silk is known.
3. Pi pin 2 vs 4 for `+5V_ADS` is TODO in CONNECTIONS — schematic uses header pin 2.
4. ADS1115 footprint is TSSOP-10 stock; bench is a breakout — swap footprint.
5. Optional AIN0 R2/D1/D2: keep or delete as a unit (23 mA × 250 Ω = 5.75 V).
6. Unused U2 AIN1–3 / ALERT and U3 A3/A4/B3/B4 are NC.
7. Re-run ERC inside KiCad after edits.
