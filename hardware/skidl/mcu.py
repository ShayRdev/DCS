"""
U1 — Raspberry Pi 4 Model B (GPIO).

Two symbol modes (same nets; pin numbers differ):
  - Stand-in Conn_01x06 (main.py / no KiCad libs): pins 1..6 = used subset only
  - Stock Connector_Generic:Conn_02x20_Odd_Even (schematic.py): real 40-pin header

Used header pins (CONNECTIONS.md):
  1 = 3V3, 2 = 5V (or 4 — TODO which), 3 = SDA GPIO2, 5 = SCL GPIO3,
  6 = GND, 11 = GPIO17 optional (NC in permanent build)
"""

from __future__ import annotations

from skidl import Net

from parts import Conn_01x06 as _Conn_01x06
from parts import nc_net


# Physical Pi header pins we wire (Odd_Even numbering matches silk).
PI_HEADER_USED = {
    1: "3V3",
    2: "5V",
    3: "SDA_GPIO2",
    5: "SCL_GPIO3",
    6: "GND",
    11: "GPIO17_optional",
}


def build_mcu(v33, v5, gnd, *, Conn_01x06=None, Conn_02x20_Odd_Even=None, use_40pin_header=False):
    """
    If use_40pin_header=True, instantiate Conn_02x20_Odd_Even and connect by
    physical header pin numbers. Otherwise use Conn_01x06 stand-in (default).
    """
    i2c_sda_3v3 = Net("I2C_SDA_3V3")
    i2c_scl_3v3 = Net("I2C_SCL_3V3")

    if use_40pin_header:
        if Conn_02x20_Odd_Even is None:
            raise ValueError("Conn_02x20_Odd_Even required when use_40pin_header=True")
        u1 = Conn_02x20_Odd_Even()
        u1.ref = "U1"
        u1.value = "RaspberryPi4_Model_B"
        u1.fields["Symbol"] = "Connector_Generic:Conn_02x20_Odd_Even"
        u1.fields["Note"] = (
            "40-pin header; pin2 vs pin4 for +5V_ADS is TODO in CONNECTIONS — using pin 2"
        )

        u1[1] += v33
        u1[2] += v5  # TODO: pin 2 vs 4 — same net either way; pin 2 chosen
        u1[3] += i2c_sda_3v3
        u1[5] += i2c_scl_3v3
        u1[6] += gnd
        # Optional pump/relay — CONNECTIONS: likely unwired; leave NC
        u1[11] += nc_net(u1)

        used = {1, 2, 3, 5, 6, 11}
        for pin in u1.pins:
            try:
                n = int(pin.num)
            except (TypeError, ValueError):
                continue
            if n not in used:
                pin += nc_net(u1)
    else:
        Conn_01x06 = Conn_01x06 or _Conn_01x06
        u1 = Conn_01x06()
        u1.ref = "U1"
        u1.value = "RaspberryPi4_Model_B_GPIO_subset"
        # Document physical header mapping in fields
        u1.fields["ConnPin1"] = "HDR1_3V3"
        u1.fields["ConnPin2"] = "HDR2or4_5V"
        u1.fields["ConnPin3"] = "HDR3_GPIO2_SDA"
        u1.fields["ConnPin4"] = "HDR5_GPIO3_SCL"
        u1.fields["ConnPin5"] = "HDR6_GND"
        u1.fields["ConnPin6"] = "HDR11_GPIO17_optional"

        u1[1] += v33
        u1[2] += v5
        u1[3] += i2c_sda_3v3
        u1[4] += i2c_scl_3v3
        u1[5] += gnd
        # Optional pump/relay — CONNECTIONS: likely unwired; leave NC
        u1[6] += nc_net(u1)

    return {
        "U1": u1,
        "I2C_SDA_3V3": i2c_sda_3v3,
        "I2C_SCL_3V3": i2c_scl_3v3,
    }
