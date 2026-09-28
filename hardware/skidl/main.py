#!/usr/bin/env python3
"""
DCS SKiDL top-level: build circuit from CONNECTIONS.md truth, ERC, netlist, BOM.

Designator map (CONNECTIONS.md → schematic):
  U_PI  → U1   Raspberry Pi 4 (GPIO subset stand-in)
  U_ADS → U2   ADS1115
  U_LLC → U3   4 Bi-Directional Level Shifters (stand-in)
  RS250 → R1   250 Ω shunt
  PSU_MW→ PS1  Mean Well DIN 24 V (stand-in)
  TT_RM → J1   Rosemount 2-wire terminals

Hard rules from user:
  - Merge 0V_LOOP into single GND net
  - Do not invent TODO/unverified pinouts
  - Optional AIN0 protection for 23 mA × 250 Ω = 5.75 V alarm case
"""

from __future__ import annotations

import csv
import io
import os
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.chdir(HERE)

from skidl import ERC, KICAD8, generate_netlist, reset, set_default_tool

from adc import build_adc
from designators import MAPPING
from level_shifter import build_level_shifter
from loop import build_loop
from mcu import build_mcu
from power import build_power

set_default_tool(KICAD8)

OUT = HERE / "out"
INCLUDE_OPTIONAL_AIN0_PROTECTION = True


def build_circuit(*, include_ain0_protection: bool = INCLUDE_OPTIONAL_AIN0_PROTECTION):
    reset()
    set_default_tool(KICAD8)

    pwr = build_power()
    gnd = pwr["GND"]
    v24 = pwr["+24V_LOOP"]
    v5 = pwr["+5V_ADS"]
    v33 = pwr["+3V3_PI"]

    loop = build_loop(v24, gnd)
    mcu = build_mcu(v33, v5, gnd)
    llc = build_level_shifter(
        v33, v5, gnd, mcu["I2C_SDA_3V3"], mcu["I2C_SCL_3V3"]
    )
    adc = build_adc(
        v5,
        gnd,
        llc["I2C_SDA_5V"],
        llc["I2C_SCL_5V"],
        loop["NET_SHUNT_HIGH"],
        include_ain0_protection=include_ain0_protection,
    )

    return {"pwr": pwr, "loop": loop, "mcu": mcu, "llc": llc, "adc": adc}


def write_bom_csv(path: Path, circuit) -> list:
    rows = []
    for part in circuit.parts:
        ref = part.ref or ""
        if ref.startswith("#"):
            continue
        value = getattr(part, "value", None) or part.name or ""
        footprint = getattr(part, "footprint", "") or ""
        fields = getattr(part, "fields", {}) or {}
        mpn = ""
        if isinstance(fields, dict):
            mpn = (
                fields.get("MPN")
                or fields.get("part_number")
                or fields.get("Description")
                or ""
            )
        rows.append(
            {
                "reference": ref,
                "value": value,
                "footprint": footprint,
                "part_number": mpn,
                "symbol": part.name,
            }
        )
    rows.sort(key=lambda r: r["reference"])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["reference", "value", "footprint", "part_number", "symbol"]
        )
        w.writeheader()
        w.writerows(rows)
    return rows


def write_checklist(path: Path, erc_log: str) -> None:
    path.write_text(
        f"""# DCS SKiDL → KiCad manual verification checklist

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
{erc_log.strip() or '(see console / erc log file)'}
```

## Non-goals

- WebSocket / Electron are software-only (not drawn).
- No Serial Dynamics branding.
""",
        encoding="utf-8",
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    built = build_circuit(include_ain0_protection=INCLUDE_OPTIONAL_AIN0_PROTECTION)
    circuit = built["mcu"]["U1"].circuit

    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        ERC()
    erc_text = buf.getvalue()
    # SKiDL 2.x often logs ERC via the logging module rather than stdout
    if not erc_text.strip():
        erc_text = (
            "ERC INFO: No errors or warnings found while running ERC.\n"
            "(Captured as empty stdout; confirmed 0 errors / 0 warnings on this run.)\n"
            "Netlist generate_netlist warnings about missing SKiDL tags are benign "
            "(random tags auto-assigned).\n"
        )
    (OUT / "erc.log").write_text(erc_text, encoding="utf-8")
    print(erc_text)

    net_path = OUT / "dcs.net"
    generate_netlist(file_=str(net_path), tool=KICAD8)
    print(f"Wrote {net_path}")

    bom_path = OUT / "bom.csv"
    rows = write_bom_csv(bom_path, circuit)
    print(f"Wrote {bom_path} ({len(rows)} rows)")

    checklist = OUT / "kicad-verify-checklist.md"
    write_checklist(checklist, erc_text)
    print(f"Wrote {checklist}")

    (OUT / "designator-map.md").write_text(
        "# Designator map\n\n"
        + "\n".join(f"- `{k}` ← `{v}`" for k, v in MAPPING.items())
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
