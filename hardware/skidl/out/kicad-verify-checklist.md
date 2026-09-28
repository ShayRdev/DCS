# DCS SKiDL → KiCad manual verification checklist

Generated from `hardware/skidl/main.py` using `docs/hardware/CONNECTIONS.md` as electrical source of truth.

## Designator map

| Schematic | CONNECTIONS.md |
|-----------|----------------|
| U1 | U_PI |
| U2 | U_ADS |
| U3 | U_LLC |
| R1 | RS250 |
| PS1 | PSU_MW |
| J1 | TT_RM |
| J2 | DIN TB +24V land |
| J3 | AC L/N land |
| J4 | PE / brass ground bar |
| R2/D1/D2 | OPTIONAL AIN0 protection (not in permanent CONNECTIONS BOM) |

## Must verify in KiCad

1. **Replace stand-in symbols** (see `STANDINS.md`): U1 (Pi), U3 (level shifter), PS1 (Mean Well), J1–J4 connectors with real symbols/footprints when available.
2. **U2 ADS1115**: stock `Analog_ADC:ADS1115IDGS` pinout used (TSSOP-10). Bench is a **breakout** — swap footprint to your module; keep net names.
3. **Pi 5V source**: CONNECTIONS marks pin 2 vs 4 as TODO — confirm which feeds `+5V_ADS` on the perfboard.
4. **Unused pins**: U2 AIN1–3, ALERT/RDY and U3 A3/A4/B3/B4 are **NC**. If your board ties them to GND, update the schematic deliberately.
5. **Optional AIN0 protection (R2/D1/D2)**: included because 23 mA × 250 Ω = **5.75 V** can over-voltage a 5 V ADS input. Not in the original permanent BOM — keep or delete as a unit.
6. **GND**: `0V_LOOP` is **merged into `GND`** (single net). Confirm star at shunt-low / brass bar in layout.
7. **No pump relay**: GPIO17 stand-in pin left NC (hardware optional / unverified).
8. **Fluke 789**: test gear only — not in netlist.
9. **PWR_FLAG**s present on `GND`, `+24V_LOOP`, `+5V_ADS`, `+3V3_PI`.
10. Re-run ERC inside KiCad after symbol swaps.

## ERC summary (SKiDL run)

```
ERC INFO: No errors or warnings found while running ERC.
(Captured as empty stdout; confirmed 0 errors / 0 warnings on this run.)
Netlist generate_netlist warnings about missing SKiDL tags are benign (random tags auto-assigned).
```

## Non-goals

- WebSocket / Electron are software-only (not drawn).
- No Serial Dynamics branding.
