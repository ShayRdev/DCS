"""
U2 — ADS1115 (+ optional AIN0 input protection).

Chip pinout mirrors KiCad Analog_ADC:ADS1115IDGS (TSSOP-10).
Bench uses a breakout exposing the same net names (CONNECTIONS.md).

Unused AIN1–AIN3: NC (CONNECTIONS TODO — do not invent GND ties).
ALERT/RDY: NC (unused in software).
ADDR → GND ⇒ I²C 0x48.
"""

from __future__ import annotations

from skidl import Net

from parts import ADS1115, D, R, nc_net


def build_adc(v5, gnd, i2c_sda_5v, i2c_scl_5v, net_shunt_high, *, include_ain0_protection=True):
    """
    OPTIONAL AIN0 protection (R2 + D1 + D2):
      Rosemount alarm current can reach ~23 mA → 23e-3 * 250 = 5.75 V across
      the shunt, which exceeds a 5 V-powered ADS1115 analog input absolute max
      (typically VDD+0.3V). Series resistor + clamp diodes to +5V_ADS / GND
      limit AIN0. Marked OPTIONAL — not in the permanent CONNECTIONS.md BOM.
    """
    u2 = ADS1115()
    u2.ref = "U2"
    u2.value = "ADS1115"
    u2.fields["I2C_addr"] = "0x48"
    u2.fields["PGA"] = "+/-6.144V"
    u2.fields["Note"] = "Breakout on bench; symbol=TSSOP-10 stock mirror"

    u2["VDD"] += v5
    u2["GND"] += gnd
    u2["SDA"] += i2c_sda_5v
    u2["SCL"] += i2c_scl_5v
    u2["ADDR"] += gnd

    nc = nc_net(u2)
    # Unused channels / alert — NC (do not invent ties)
    u2["AIN1"] += nc
    u2["AIN2"] += nc
    u2["AIN3"] += nc
    u2["ALERT/RDY"] += nc

    protection = {}
    if include_ain0_protection:
        r2 = R(value="1k")
        r2.ref = "R2"
        r2.fields["Description"] = "OPTIONAL AIN0 series — alarm 23mA*250R=5.75V clamp path"
        r2.fields["Optional"] = "yes"

        d_hi = D(value="1N4148")
        d_hi.ref = "D1"
        d_hi.fields["Description"] = "OPTIONAL clamp AIN0 to +5V_ADS (A=AIN, K=+5V)"
        d_hi.fields["Optional"] = "yes"

        d_lo = D(value="1N4148")
        d_lo.ref = "D2"
        d_lo.fields["Description"] = "OPTIONAL clamp AIN0 to GND (K=AIN, A=GND)"
        d_lo.fields["Optional"] = "yes"

        # Clamp AIN0_PROT between GND and +5V_ADS (Device.D: pin1=K, pin2=A):
        #   D1 to +5V: A→AIN, K→+5V
        #   D2 to GND: K→AIN, A→GND

        ain_prot = Net("AIN0_PROT")
        r2[1] += net_shunt_high
        r2[2] += ain_prot
        u2["AIN0"] += ain_prot

        d_hi[2] += ain_prot  # A
        d_hi[1] += v5  # K → +5V

        d_lo[1] += ain_prot  # K → AIN
        d_lo[2] += gnd  # A → GND

        protection = {"R2": r2, "D1": d_hi, "D2": d_lo, "AIN0_PROT": ain_prot}
    else:
        u2["AIN0"] += net_shunt_high

    return {"U2": u2, **protection}
