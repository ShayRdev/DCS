# Hardware notes — DCS

Revision **A** · 2026-09-27 · companions: `schematic-overview.svg` (SCH-DCS-001), `pinout.svg` (SCH-DCS-002)

## What this measured on the bench

A **Rosemount** 2-wire **temperature transmitter** (4–20 mA) was wired through a precision shunt into an **ADS1115** ADC on a Raspberry Pi I²C bus. The Pi service printed live temperature / loop current / shunt voltage in the terminal and streamed the same readings to the Electron desktop app over WebSocket.

This is a personal portfolio build — not a commercial product brand.

## Signal path

```
Rosemount TT (4–20 mA)
    → 24 VDC loop supply
    → 100 Ω shunt
    → voltage into ADS1115 AIN0
    → I²C (Pi GPIO2/SDA, GPIO3/SCL, addr 0x48)
    → raspberry-pi/dcs_server.py
         ├─ terminal printout
         └─ WebSocket ws://<pi-ip>:8765
              → desktop-app (DCS)
```

## Parts

| Part | Role |
|---|---|
| Raspberry Pi (I²C capable) | Runs `dcs_server.py` |
| ADS1115 breakout | 16-bit ADC |
| 100 Ω ±0.1% shunt | 4–20 mA → 0.4–2.0 V |
| 24 VDC supply | Transmitter loop power |
| Rosemount temperature transmitter | 4–20 mA process input |
| Adafruit 757 LLC (optional) | Only if ADS1115 is run at 5 V |
| Dupont / cobbler **or** soldered proto / flex PCB | Mechanical interconnect |

## Pinout (copy)

| Pi | Signal | Destination |
|---|---|---|
| Pin 1 (3V3) | Power | ADS1115 VDD |
| Pin 3 (GPIO2) | SDA | ADS1115 SDA |
| Pin 5 (GPIO3) | SCL | ADS1115 SCL |
| Pin 6 (GND) | Ground | ADS1115 GND + shunt low |
| Pin 11 (GPIO17) | Pump relay (optional) | Relay IN (active-low boards) |

ADS1115 **ADDR → GND** ⇒ address **0x48**.

## Calibration

Default software scale (override with env / flags on the Pi service):

- 4 mA → **0 °C** (`DCS_LRV_C`)
- 20 mA → **100 °C** (`DCS_URV_C`)
- Shunt **100 Ω** (`DCS_SHUNT_OHMS`)

Match LRV/URV to the transmitter’s configured range.

## Breadboard vs soldered

**Breadboard:** Pi cobbler → ADS1115 module; shunt between AIN0 and GND; screw-terminal or clip leads to the Rosemount and 24 V supply.

**Soldered / flex PCB:** Same netlist. Mount ADS1115 + shunt on proto or a small flex/rigid board with screw terminals for the loop. Keep the shunt Kelvin connection short.

## Safety / grounding

Keep the 24 V loop return tied at a single star with ADC/Pi GND at the **shunt low** side. Prefer an isolated 24 V supply. Do not inject loop current into the Pi’s 5 V rail.

## Verify

```bash
sudo raspi-config   # Interface Options → I2C → Enable
sudo i2cdetect -y 1 # expect 0x48
cd raspberry-pi
python3 dcs_server.py
# Terminal should stream: TT  xx.xx °C   I=… mA   V=… V
```
