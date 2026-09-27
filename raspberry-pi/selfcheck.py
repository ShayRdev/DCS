#!/usr/bin/env python3
"""Quick offline check of 4–20 mA → °C math (no I²C needed)."""

from rosemount import voltage_to_loop


def main() -> None:
    for ma in (4.0, 8.0, 12.0, 16.0, 20.0):
        v = (ma / 1000.0) * 100.0
        r = voltage_to_loop(v, shunt_ohms=100.0, lrv_c=0.0, urv_c=100.0)
        print(f"{ma:5.1f} mA  →  {r.voltage_v:.3f} V  →  {r.temperature_c:6.2f} °C")


if __name__ == "__main__":
    main()
