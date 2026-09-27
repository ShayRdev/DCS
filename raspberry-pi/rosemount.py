"""
Rosemount temperature transmitter → engineering units.

Hardware path used on the bench:
  Rosemount 4–20 mA loop → precision shunt → ADS1115 AIN0 → Pi I²C

Default calibration (override with env / CLI):
  4 mA  → LRV (°C)
  20 mA → URV (°C)
  shunt = 100 Ω  → 0.4 V @ 4 mA, 2.0 V @ 20 mA (fits ±4.096 V PGA)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LoopReading:
    voltage_v: float
    current_ma: float
    temperature_c: float
    shunt_ohms: float
    lrv_c: float
    urv_c: float


def voltage_to_loop(
    voltage_v: float,
    *,
    shunt_ohms: float = 100.0,
    lrv_c: float = 0.0,
    urv_c: float = 100.0,
) -> LoopReading:
    if shunt_ohms <= 0:
        raise ValueError("shunt_ohms must be > 0")
    current_ma = (voltage_v / shunt_ohms) * 1000.0
    # Linear map 4–20 mA → LRV–URV
    span = 16.0  # mA
    frac = (current_ma - 4.0) / span
    temperature_c = lrv_c + frac * (urv_c - lrv_c)
    return LoopReading(
        voltage_v=voltage_v,
        current_ma=current_ma,
        temperature_c=temperature_c,
        shunt_ohms=shunt_ohms,
        lrv_c=lrv_c,
        urv_c=urv_c,
    )
