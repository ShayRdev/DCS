"""
U1 — Raspberry Pi 4 Model B (GPIO subset).

STAND-IN: Connector_Generic Conn_01x06 representing confirmed pins only.
Full 40-pin HAT is not drawn (CONNECTIONS lists only used BCM pins).

Pin map on this stand-in:
  1 = 3V3   (header pin 1)
  2 = 5V    (header pin 2 OR 4 — which one unverified; electrically either)
  3 = SDA   (header pin 3 / GPIO2)
  4 = SCL   (header pin 5 / GPIO3)
  5 = GND   (header pin 6)
  6 = GPIO17 (header pin 11) — optional RELAY_DRV; left NC in permanent build
"""

from __future__ import annotations

from skidl import Net

from parts import Conn_01x06, nc_net


def build_mcu(v33, v5, gnd):
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

    i2c_sda_3v3 = Net("I2C_SDA_3V3")
    i2c_scl_3v3 = Net("I2C_SCL_3V3")

    u1[1] += v33
    u1[2] += v5
    u1[3] += i2c_sda_3v3
    u1[4] += i2c_scl_3v3
    u1[5] += gnd
    # Optional pump/relay — CONNECTIONS: likely unwired; leave NC (do not invent relay)
    u1[6] += nc_net(u1)

    return {
        "U1": u1,
        "I2C_SDA_3V3": i2c_sda_3v3,
        "I2C_SCL_3V3": i2c_scl_3v3,
    }
