"""
Shared SKiDL part templates for the DCS loop schematic.

Stock KiCad libraries are preferred conceptually; this environment may not have
KICAD*_SYMBOL_DIR populated, so parts are defined with tool=SKIDL while
mirroring stock symbol names / pin functions where possible.

STAND-IN SYMBOLS (documented): see STANDINS.md and README.md
"""

from __future__ import annotations

from skidl import SKIDL, Part, Pin, TEMPLATE
from skidl.pin import pin_types


def _part(name, ref_prefix, pins, footprint="", aliases=None):
    kwargs = dict(
        tool=SKIDL,
        name=name,
        dest=TEMPLATE,
        ref_prefix=ref_prefix,
        footprint=footprint or "",
        pins=pins,
    )
    p = Part(**kwargs)
    if aliases:
        p.aliases = aliases
    return p


def nc_net(part: Part):
    """Intentional no-connect net for unused pins (skidl 2.x)."""
    return part.circuit.NC


# --- Stock-mirrored passives (Device:R, Device:D) ---

R = _part(
    "R",
    "R",
    [
        Pin(num="1", name="~", func=pin_types.PASSIVE),
        Pin(num="2", name="~", func=pin_types.PASSIVE),
    ],
    footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
)
# Mirrors KiCad Device:R

D = _part(
    "D",
    "D",
    [
        Pin(num="1", name="K", func=pin_types.PASSIVE),  # cathode
        Pin(num="2", name="A", func=pin_types.PASSIVE),  # anode
    ],
    footprint="Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal",
)
# Mirrors KiCad Device:D (K=1, A=2 in many Device.D variants — verify in KiCad)


# --- Power flag (power:PWR_FLAG) ---

PWR_FLAG = _part(
    "PWR_FLAG",
    "#FLG",
    [Pin(num="1", name="pwr", func=pin_types.PWRIN)],
    footprint="power:PWR_FLAG",  # schematic-only; KiCad treats as no PCB fab
)


# --- Generic connectors (Connector_Generic stand-ins) ---

def Conn(n_pins: int):
    """Connector_Generic:Conn_01xN stand-in."""
    pins = [Pin(num=str(i), name=str(i), func=pin_types.PASSIVE) for i in range(1, n_pins + 1)]
    return _part(
        f"Conn_01x{n_pins:02d}",
        "J",
        pins,
        footprint=f"Connector_PinHeader_2.54mm:PinHeader_1x{n_pins:02d}_P2.54mm_Vertical",
    )


Conn_01x02 = Conn(2)
Conn_01x04 = Conn(4)
Conn_01x06 = Conn(6)
Conn_01x08 = Conn(8)
Conn_01x12 = Conn(12)


# --- ADS1115 (mirrors Analog_ADC:ADS1115IDGS TSSOP-10 pinout) ---
# Pin numbers from KiCad stock ADS1015IDGS / ADS1115IDGS:
# 1 ADDR, 2 ALERT/RDY, 3 GND, 4 AIN0, 5 AIN1, 6 AIN2, 7 AIN3, 8 VDD, 9 SDA, 10 SCL

ADS1115 = _part(
    "ADS1115",
    "U",
    [
        Pin(num="1", name="ADDR", func=pin_types.INPUT),
        Pin(num="2", name="ALERT/RDY", func=pin_types.OUTPUT),
        Pin(num="3", name="GND", func=pin_types.PWRIN),
        Pin(num="4", name="AIN0", func=pin_types.INPUT),
        Pin(num="5", name="AIN1", func=pin_types.INPUT),
        Pin(num="6", name="AIN2", func=pin_types.INPUT),
        Pin(num="7", name="AIN3", func=pin_types.INPUT),
        Pin(num="8", name="VDD", func=pin_types.PWRIN),
        Pin(num="9", name="SDA", func=pin_types.BIDIR),
        Pin(num="10", name="SCL", func=pin_types.INPUT),
    ],
    footprint="Package_SO:TSSOP-10_3x3mm_P0.5mm",
)
# Stock mirror: Analog_ADC:ADS1115IDGS — breakout boards expose the same net names.
# Bench uses a breakout; footprint may be replaced with a module footprint in KiCad.
