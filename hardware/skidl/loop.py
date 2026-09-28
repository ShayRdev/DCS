"""
4–20 mA loop: Rosemount (J1) + 250 Ω shunt (R1).

Path (CONNECTIONS.md):
  +24V_LOOP → TT+ → TT− → shunt high → NET_SHUNT_HIGH → ADS AIN0
                         → shunt low  → GND
"""

from __future__ import annotations

from skidl import Net

from parts import Conn_01x02 as _Conn_01x02
from parts import R as _R


def build_loop(v24, gnd, *, Conn_01x02=None, R=None):
    """
    J1 = Rosemount 2-wire terminals (Conn_01x02).
      1 = +
      2 = −
    R1 = 250 Ω ±0.1% shunt
      1 = high (NET_SHUNT_HIGH)
      2 = low  (GND)
    """
    Conn_01x02 = Conn_01x02 or _Conn_01x02
    R = R or _R

    j1 = Conn_01x02()
    j1.ref = "J1"
    j1.value = "Rosemount_2wire_TT"

    r1 = R(value="250")
    r1.ref = "R1"
    r1.fields["Tolerance"] = "0.1%"
    r1.fields["Description"] = "Shunt 250R — 4-20mA to 1-5V (CONNECTIONS.md RS250)"

    net_shunt_high = Net("NET_SHUNT_HIGH")
    # NET_LOOP_RETURN is the same node as shunt high (series into shunt)
    # Keep one net name per CONNECTIONS checklist: NET_SHUNT_HIGH

    j1[1] += v24  # TT +
    j1[2] += net_shunt_high  # TT − → shunt high
    r1[1] += net_shunt_high
    r1[2] += gnd

    return {
        "J1": j1,
        "R1": r1,
        "NET_SHUNT_HIGH": net_shunt_high,
    }
