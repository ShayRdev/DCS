"""
Power: Mean Well DIN 24 V (PS1) + rails + PWR_FLAG.

CONNECTIONS.md: 0V_LOOP is merged into a single GND net (user hard requirement).
AC terminal silk on PS1 is TODO/unverified — pins are generic 1..4 only.
"""

from __future__ import annotations

from skidl import Net, POWER

from parts import Conn_01x02, Conn_01x04, PWR_FLAG


def build_power():
    """
    Returns dict of nets and PS1 / AC / PE connectors.

    PS1 pin assignment (generic stand-in — NOT Mean Well silk):
      1 = AC_L (input)
      2 = AC_N (input)
      3 = +V  → +24V_LOOP
      4 = −V  → GND  (was 0V_LOOP; merged)
    """
    gnd = Net("GND")
    gnd.drive = POWER

    v24 = Net("+24V_LOOP")
    v24.drive = POWER

    v5 = Net("+5V_ADS")
    v5.drive = POWER

    v33 = Net("+3V3_PI")
    v33.drive = POWER

    # AC inlet landing (J3) — labels L/N only as functional nets
    j_ac = Conn_01x02()
    j_ac.ref = "J3"
    j_ac.value = "AC_LN_landing"
    ac_l = Net("AC_L")
    ac_n = Net("AC_N")
    j_ac[1] += ac_l
    j_ac[2] += ac_n

    # PS1 — Mean Well family stand-in (Connector_Generic)
    ps1 = Conn_01x04()
    ps1.ref = "PS1"
    ps1.value = "MeanWell_DIN_24V_HDR-15-24_family"
    ps1[1] += ac_l
    ps1[2] += ac_n
    ps1[3] += v24
    ps1[4] += gnd  # −V → GND (merged 0V_LOOP)

    # PE / brass ground bar landing — electrically bonded to star GND
    # (CONNECTIONS: PE wire lands on brass bar with signal GND).
    j_pe = Conn_01x02()
    j_pe.ref = "J4"
    j_pe.value = "PE_brass_ground_bar"
    j_pe.fields["Note"] = "Pin1=PE land, Pin2=signal GND land; both star to GND"
    j_pe[1] += gnd
    j_pe[2] += gnd

    # Optional DIN face for +24 field land (documentation aid)
    j24 = Conn_01x02()
    j24.ref = "J2"
    j24.value = "DIN_TB_+24V_LOOP"
    j24[1] += v24
    j24[2] += gnd

    # PWR_FLAGs so ERC treats rails as driven
    for net in (gnd, v24, v5, v33):
        flg = PWR_FLAG()
        flg[1] += net

    return {
        "GND": gnd,
        "+24V_LOOP": v24,
        "+5V_ADS": v5,
        "+3V3_PI": v33,
        "AC_L": ac_l,
        "AC_N": ac_n,
        "PS1": ps1,
        "J2": j24,
        "J3": j_ac,
        "J4": j_pe,
    }
