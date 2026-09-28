"""
U3 — Blue 4 Bi-Directional Level Shifters module.

Symbol: Connector_Generic Conn_01x12 matching module silk order
(CONNECTIONS.md photo): LV, A1, A2, A3, A4, GND | HV, B1, B2, B3, B4, GND

Used: LV, HV, GND×2, A1/A2, B1/B2.
Unused A3/A4/B3/B4: left NC (CONNECTIONS: TODO whether tied to GND — do not invent).
"""

from __future__ import annotations

from skidl import Net

from parts import Conn_01x12 as _Conn_01x12
from parts import nc_net


def build_level_shifter(v33, v5, gnd, i2c_sda_3v3, i2c_scl_3v3, *, Conn_01x12=None):
    Conn_01x12 = Conn_01x12 or _Conn_01x12

    u3 = Conn_01x12()
    u3.ref = "U3"
    u3.value = "4_BiDirectional_Level_Shifters"
    u3.fields["Silk"] = "LV A1 A2 A3 A4 GND | HV B1 B2 B3 B4 GND"
    u3.fields["Symbol"] = "Connector_Generic:Conn_01x12"

    i2c_sda_5v = Net("I2C_SDA_5V")
    i2c_scl_5v = Net("I2C_SCL_5V")
    nc = nc_net(u3)

    # LV edge
    u3[1] += v33  # LV
    u3[2] += i2c_sda_3v3  # A1
    u3[3] += i2c_scl_3v3  # A2
    u3[4] += nc  # A3 unused
    u3[5] += nc  # A4 unused
    u3[6] += gnd  # GND (LV)

    # HV edge
    u3[7] += v5  # HV
    u3[8] += i2c_sda_5v  # B1
    u3[9] += i2c_scl_5v  # B2
    u3[10] += nc  # B3 unused
    u3[11] += nc  # B4 unused
    u3[12] += gnd  # GND (HV)

    return {
        "U3": u3,
        "I2C_SDA_5V": i2c_sda_5v,
        "I2C_SCL_5V": i2c_scl_5v,
    }
