# Stand-in symbols

This SKiDL project runs without a local `KICAD*_SYMBOL_DIR` by defining parts in `parts.py` (`tool=SKIDL`) that **mirror** stock KiCad libraries. Replace stand-ins in KiCad when you have the real symbols.

| Ref | Value / role | Stand-in? | Preferred stock symbol when available |
|-----|--------------|-----------|----------------------------------------|
| R1, R2 | Resistors | No (mirrors Device:R) | `Device:R` |
| D1, D2 | Diodes | No (mirrors Device:D) | `Device:D` |
| U2 | ADS1115 | Pinout mirrors stock IC | `Analog_ADC:ADS1115IDGS` (TSSOP-10); bench is a **breakout** — change footprint |
| U1 | Raspberry Pi 4 GPIO subset | **YES** — `Conn_01x06` | MCU/Raspberry Pi symbol or keep Conn with pin notes |
| U3 | 4 Bi-Directional Level Shifters | **YES** — `Conn_01x12` | Custom module symbol; silk order LV/A1–A4/GND/HV/B1–B4/GND |
| PS1 | Mean Well DIN 24 V | **YES** — `Conn_01x04` | PSU symbol; silk L/N/+V/−V is TODO in CONNECTIONS |
| J1 | Rosemount TT | **YES** — `Conn_01x02` | Terminal block / connector |
| J2–J4 | DIN/AC/PE lands | **YES** — `Conn_01x02` | Terminal blocks |
| #FLGn | PWR_FLAG | Mirrors `power:PWR_FLAG` | `power:PWR_FLAG` |

## U1 pin map (stand-in)

| U1 pin | Net | Pi header |
|--------|-----|-----------|
| 1 | +3V3_PI | pin 1 |
| 2 | +5V_ADS | pin 2 **or** 4 (TODO which) |
| 3 | I2C_SDA_3V3 | pin 3 GPIO2 |
| 4 | I2C_SCL_3V3 | pin 5 GPIO3 |
| 5 | GND | pin 6 |
| 6 | NC | pin 11 GPIO17 optional |

## U3 pin map (stand-in)

| U3 pin | Silk | Net |
|--------|------|-----|
| 1 | LV | +3V3_PI |
| 2 | A1 | I2C_SDA_3V3 |
| 3 | A2 | I2C_SCL_3V3 |
| 4–5 | A3–A4 | NC |
| 6 | GND | GND |
| 7 | HV | +5V_ADS |
| 8 | B1 | I2C_SDA_5V |
| 9 | B2 | I2C_SCL_5V |
| 10–11 | B3–B4 | NC |
| 12 | GND | GND |

## PS1 pin map (stand-in — not Mean Well silk)

| PS1 pin | Net |
|---------|-----|
| 1 | AC_L |
| 2 | AC_N |
| 3 | +24V_LOOP |
| 4 | GND (merged 0V_LOOP) |
