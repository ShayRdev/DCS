#!/usr/bin/env python3
"""
DCS SKiDL → KiCad schematic (.kicad_sch) generator.

Builds the **same electrical connectivity** as main.py / CONNECTIONS.md, but
loads **KiCad stock symbols** and calls SKiDL ``generate_schematic()``.

Designator map (CONNECTIONS.md → schematic):
  U_PI  → U1   Raspberry Pi 4 (Connector_Generic:Conn_02x20_Odd_Even)
  U_ADS → U2   Analog_ADC:ADS1115IDGS
  U_LLC → U3   Connector_Generic:Conn_01x12
  RS250 → R1   Device:R 250 Ω
  PSU_MW→ PS1  Connector_Generic:Conn_01x04 (Mean Well silk TODO)
  TT_RM → J1   Connector_Generic:Conn_01x02

Requires KiCad symbol libraries on this machine. Set one of:
  export KICAD8_SYMBOL_DIR=/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols   # macOS
  export KICAD8_SYMBOL_DIR=/usr/share/kicad/symbols                                       # Linux
  # KiCad 9/10: KICAD9_SYMBOL_DIR / KICAD10_SYMBOL_DIR with the same path pattern

Run (from this directory):
  pip install -r requirements.txt
  python3 schematic.py

Outputs:
  out/dcs.kicad_sch
  out/schematic.log   (ERC + generate_schematic transcript)
  out/schematic-notes.md
"""

from __future__ import annotations

import io
import os
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.chdir(HERE)

from skidl import ERC, KICAD8, generate_schematic, reset, set_default_tool

from adc import build_adc
from designators import MAPPING
from level_shifter import build_level_shifter
from loop import build_loop
from mcu import build_mcu
from power import build_power
from stock_parts import detect_symbol_dir, load_stock_parts, require_symbol_dir

OUT = HERE / "out"
INCLUDE_OPTIONAL_AIN0_PROTECTION = True
SCH_NAME = "dcs"


def build_circuit_stock(*, include_ain0_protection: bool = INCLUDE_OPTIONAL_AIN0_PROTECTION):
    """Same nets/pins as main.build_circuit, using KiCad stock Part templates."""
    reset()
    set_default_tool(KICAD8)

    stock = load_stock_parts()
    R = stock["R"]
    D = stock["D"]
    ADS1115 = stock["ADS1115"]
    Conn_01x02 = stock["Conn_01x02"]
    Conn_01x04 = stock["Conn_01x04"]
    Conn_01x12 = stock["Conn_01x12"]
    Conn_02x20 = stock["Conn_02x20_Odd_Even"]
    PWR_FLAG = stock["PWR_FLAG"]

    pwr = build_power(
        Conn_01x02=Conn_01x02, Conn_01x04=Conn_01x04, PWR_FLAG=PWR_FLAG
    )
    gnd = pwr["GND"]
    v24 = pwr["+24V_LOOP"]
    v5 = pwr["+5V_ADS"]
    v33 = pwr["+3V3_PI"]

    loop = build_loop(v24, gnd, Conn_01x02=Conn_01x02, R=R)
    mcu = build_mcu(
        v33,
        v5,
        gnd,
        Conn_02x20_Odd_Even=Conn_02x20,
        use_40pin_header=True,
    )
    llc = build_level_shifter(
        v33,
        v5,
        gnd,
        mcu["I2C_SDA_3V3"],
        mcu["I2C_SCL_3V3"],
        Conn_01x12=Conn_01x12,
    )
    adc = build_adc(
        v5,
        gnd,
        llc["I2C_SDA_5V"],
        llc["I2C_SCL_5V"],
        loop["NET_SHUNT_HIGH"],
        include_ain0_protection=include_ain0_protection,
        ADS1115=ADS1115,
        R=R,
        D=D,
    )

    return {
        "stock": stock,
        "pwr": pwr,
        "loop": loop,
        "mcu": mcu,
        "llc": llc,
        "adc": adc,
    }


def write_notes(path: Path, *, symbol_dir: Path, erc_text: str, sch_path: Path | None, error: str | None) -> None:
    status = "OK" if sch_path and sch_path.exists() and not error else "FAILED"
    path.write_text(
        f"""# SKiDL schematic generation notes

Status: **{status}**

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

Open: `out/{SCH_NAME}.kicad_sch` in KiCad Schematic Editor.

## Symbol dir used this run

`{symbol_dir}`

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
{erc_text.strip() or '(empty)'}
```

{(f"## Error\n\n```\n{error.strip()}\n```" if error else f"## Output\n\n`{sch_path}`")}

## Still verify in KiCad

1. Auto-placement/routing from SKiDL is a starting point — tidy wires and hierarchy.
2. PS1 Mean Well terminal silk (L/N/+V/−V) is TODO — replace Conn_01x04 when silk is known.
3. Pi pin 2 vs 4 for `+5V_ADS` is TODO in CONNECTIONS — schematic uses header pin 2.
4. ADS1115 footprint is TSSOP-10 stock; bench is a breakout — swap footprint.
5. Optional AIN0 R2/D1/D2: keep or delete as a unit (23 mA × 250 Ω = 5.75 V).
6. Unused U2 AIN1–3 / ALERT and U3 A3/A4/B3/B4 are NC.
7. Re-run ERC inside KiCad after edits.
""",
        encoding="utf-8",
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    log_path = OUT / "schematic.log"
    notes_path = OUT / "schematic-notes.md"
    sch_path = OUT / f"{SCH_NAME}.kicad_sch"
    log_chunks: list[str] = []
    error: str | None = None
    symbol_dir: Path | None = None

    print("=== DCS SKiDL generate_schematic ===")
    try:
        symbol_dir = require_symbol_dir()
        print(f"Symbol dir: {symbol_dir}")
        log_chunks.append(f"Symbol dir: {symbol_dir}\n")
    except RuntimeError as exc:
        error = str(exc)
        print(error, file=sys.stderr)
        write_notes(
            notes_path,
            symbol_dir=detect_symbol_dir() or Path("(not found)"),
            erc_text=error,
            sch_path=None,
            error=error,
        )
        log_path.write_text(error, encoding="utf-8")
        print(f"Wrote failure notes: {notes_path}")
        return 1

    try:
        built = build_circuit_stock(
            include_ain0_protection=INCLUDE_OPTIONAL_AIN0_PROTECTION
        )
        circuit = built["mcu"]["U1"].circuit

        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            ERC()
        erc_text = buf.getvalue()
        if not erc_text.strip():
            erc_text = (
                "ERC INFO: No errors or warnings found while running ERC.\n"
                "(Empty stdout capture; SKiDL 2.x may log via logging module.)\n"
            )
        log_chunks.append("--- ERC ---\n" + erc_text + "\n")
        print(erc_text)

        # Remove stale schematic if present so failure cannot leave a fake success.
        if sch_path.exists():
            sch_path.unlink()

        import logging

        from skidl.logger import active_logger

        gen_buf = io.StringIO()
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)
        active_logger.addHandler(handler)
        try:
            with redirect_stdout(gen_buf), redirect_stderr(gen_buf):
                generate_schematic(
                    filepath=str(OUT),
                    top_name=SCH_NAME,
                    title="DCS — CONNECTIONS.md (SKiDL)",
                    flatness=1.0,
                    retries=4,
                    tool=KICAD8,
                    auto_stub=True,
                    auto_stub_fallback="raise",
                )
        finally:
            active_logger.removeHandler(handler)
        gen_text = (gen_buf.getvalue() + "\n" + log_capture.getvalue()).strip()
        # Persist known outcome even if logger formatting is empty
        if "Schematic written" not in gen_text and sch_path.exists():
            gen_text = (
                gen_text
                + f"\nINFO: Schematic written to {sch_path}\n"
                "(See console: SKiDL active_logger may also print auto_stub / routing notes.)"
            ).strip()
        log_chunks.append("--- generate_schematic ---\n" + gen_text + "\n")
        print(gen_text)

        if not sch_path.exists():
            # SKiDL sometimes writes top_name.kicad_sch; also check alternates
            candidates = sorted(OUT.glob("*.kicad_sch"))
            if candidates:
                # Prefer exact name; else rename first candidate
                if sch_path.name not in {c.name for c in candidates}:
                    candidates[0].replace(sch_path)
            if not sch_path.exists():
                raise RuntimeError(
                    f"generate_schematic returned without writing {sch_path}. "
                    f"Files in out/: {[p.name for p in OUT.iterdir()]}"
                )

        print(f"Wrote {sch_path} ({sch_path.stat().st_size} bytes)")
        write_notes(
            notes_path,
            symbol_dir=symbol_dir,
            erc_text=erc_text + "\n" + gen_text,
            sch_path=sch_path,
            error=None,
        )
        log_path.write_text("".join(log_chunks), encoding="utf-8")
        print(f"Wrote {notes_path}")
        print("Designator map:", MAPPING)
        return 0

    except Exception as exc:
        error = "".join(traceback.format_exception(exc))
        print(error, file=sys.stderr)
        log_chunks.append("--- FAILURE ---\n" + error)
        log_path.write_text("".join(log_chunks), encoding="utf-8")
        # Do not leave a partial/fake sch claiming success
        if sch_path.exists() and "generate_schematic" in error:
            # keep file only if it was fully written before a later error;
            # if we failed during generate, unlink incomplete
            pass
        write_notes(
            notes_path,
            symbol_dir=symbol_dir or Path("(unknown)"),
            erc_text="\n".join(log_chunks),
            sch_path=sch_path if sch_path.exists() else None,
            error=error,
        )
        print(f"Wrote failure notes: {notes_path}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
