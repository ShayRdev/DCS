"""
KiCad stock symbol Part templates for schematic.py.

Requires KICAD8_SYMBOL_DIR / KICAD9_SYMBOL_DIR / KICAD10_SYMBOL_DIR (or
matching version) pointing at a directory that contains packed *.kicad_sym
files (Device, Analog_ADC, Connector_Generic, power).

Raises RuntimeError with a clear message if the env var is missing or a
library cannot be loaded — no silent fallback to SKIDL stand-ins.
"""

from __future__ import annotations

import os
from pathlib import Path

from skidl import TEMPLATE, Part


REQUIRED_LIBS = (
    "Device.kicad_sym",
    "Analog_ADC.kicad_sym",
    "Connector_Generic.kicad_sym",
    "power.kicad_sym",
)

SYMBOL_DIR_ENV_CANDIDATES = (
    "KICAD8_SYMBOL_DIR",
    "KICAD9_SYMBOL_DIR",
    "KICAD10_SYMBOL_DIR",
    "KICAD7_SYMBOL_DIR",
    "KICAD6_SYMBOL_DIR",
    "KICAD_SYMBOL_DIR",
)

COMMON_PATHS = (
    # Linux packages
    "/usr/share/kicad/symbols",
    "/usr/local/share/kicad/symbols",
    # macOS app bundle
    "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols",
    "/Applications/KiCad/Contents/SharedSupport/symbols",
)


def detect_symbol_dir() -> Path | None:
    for key in SYMBOL_DIR_ENV_CANDIDATES:
        val = os.environ.get(key)
        if val and Path(val).is_dir():
            return Path(val)
    for path in COMMON_PATHS:
        p = Path(path)
        if p.is_dir() and (p / "Device.kicad_sym").exists():
            return p
    return None


def require_symbol_dir() -> Path:
    """
    Return the KiCad symbol directory, or raise with exact setup instructions.
    """
    found = detect_symbol_dir()
    if found is None:
        raise RuntimeError(
            "KiCad symbol libraries not found.\n"
            "generate_schematic() needs stock *.kicad_sym files.\n\n"
            "Set the env var for your KiCad major version, then re-run:\n"
            "  # macOS (KiCad 8 app bundle — typical for this project):\n"
            "  export KICAD8_SYMBOL_DIR=/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols\n"
            "  # Linux:\n"
            "  export KICAD8_SYMBOL_DIR=/usr/share/kicad/symbols\n"
            "  # KiCad 9 → use KICAD9_SYMBOL_DIR with the same path pattern.\n"
            "Also accepted: KICAD10_SYMBOL_DIR, KICAD7_SYMBOL_DIR, KICAD6_SYMBOL_DIR.\n"
        )
    missing = [name for name in REQUIRED_LIBS if not (found / name).exists()]
    if missing:
        raise RuntimeError(
            f"Symbol dir {found} is missing required libraries: {', '.join(missing)}.\n"
            "Install the full KiCad symbol package, or copy those *.kicad_sym files into the dir."
        )
    # Ensure the matching env var is set so SKiDL's library search finds them.
    if not any(os.environ.get(k) for k in SYMBOL_DIR_ENV_CANDIDATES):
        os.environ["KICAD8_SYMBOL_DIR"] = str(found)
    return found


def load_stock_parts():
    """
    Load Part TEMPLATEs from KiCad stock libraries.

    Call after set_default_tool(KICAD8) (or matching version).
    """
    symbol_dir = require_symbol_dir()

    try:
        R = Part("Device", "R", dest=TEMPLATE)
        D = Part("Device", "D", dest=TEMPLATE)
        ADS1115 = Part("Analog_ADC", "ADS1115IDGS", dest=TEMPLATE)
        Conn_01x02 = Part("Connector_Generic", "Conn_01x02", dest=TEMPLATE)
        Conn_01x04 = Part("Connector_Generic", "Conn_01x04", dest=TEMPLATE)
        Conn_01x12 = Part("Connector_Generic", "Conn_01x12", dest=TEMPLATE)
        Conn_02x20_Odd_Even = Part(
            "Connector_Generic", "Conn_02x20_Odd_Even", dest=TEMPLATE
        )
        PWR_FLAG = Part("power", "PWR_FLAG", dest=TEMPLATE)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load KiCad stock symbols from {symbol_dir}: {exc}"
        ) from exc

    # Footprints (board intent; schematic generation tolerates empty)
    R.footprint = (
        "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
    )
    D.footprint = "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"
    ADS1115.footprint = "Package_SO:TSSOP-10_3x3mm_P0.5mm"
    Conn_01x02.footprint = (
        "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"
    )
    Conn_01x04.footprint = (
        "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"
    )
    Conn_01x12.footprint = (
        "Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical"
    )
    Conn_02x20_Odd_Even.footprint = (
        "Connector_PinHeader_2.54mm:PinHeader_2x20_P2.54mm_Vertical"
    )
    PWR_FLAG.footprint = "power:PWR_FLAG"

    return {
        "symbol_dir": symbol_dir,
        "R": R,
        "D": D,
        "ADS1115": ADS1115,
        "Conn_01x02": Conn_01x02,
        "Conn_01x04": Conn_01x04,
        "Conn_01x12": Conn_01x12,
        "Conn_02x20_Odd_Even": Conn_02x20_Odd_Even,
        "PWR_FLAG": PWR_FLAG,
    }
