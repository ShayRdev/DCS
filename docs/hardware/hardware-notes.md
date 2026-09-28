# Hardware notes — DCS

Revision **C** · 2026-09-27 · companions: `schematic-blocks.svg` / `.pdf` (**SCH-DCS-003** rev H, preferred human-readable), `schematic-overview.pdf` (SCH-DCS-001), `pinout.pdf` (SCH-DCS-002)

Open the **SVG/PDF** drawings in this folder (GitHub does not always inline PDF).

**Wire-level truth:** [`CONNECTIONS.md`](CONNECTIONS.md)  
**Human-readable schematic:** [`schematic-blocks.svg`](schematic-blocks.svg) / [`schematic-blocks.pdf`](schematic-blocks.pdf)

## What this measured on the bench

A **Rosemount** 2-wire **temperature transmitter** (4–20 mA) was wired through a **250 Ω** shunt into an **ADS1115** (5 V) on a Raspberry Pi 4. I²C crossed a blue **4 Bi-Directional Level Shifters** module on a green perfboard HAT. The Pi printed `V` / `I` / `%Span` in the terminal and streamed readings to the Electron desktop app over WebSocket. Loop points were checked with a **Fluke 789** (e.g. 8.000 mA / 25.0% OUTPUT).

This is a personal portfolio build — not a commercial product brand.

## Signal path

```
Rosemount TT (4–20 mA)
    → 24 VDC loop supply (Mean Well DIN-rail)
    → 250 Ω shunt  (1–5 V)
    → ADS1115 AIN0 @ 5 V
    → I²C via 4-ch bi-directional level shifter
    → Raspberry Pi 4 (GPIO2/SDA, GPIO3/SCL, addr 0x48)
    → raspberry-pi/dcs_server.py
         ├─ terminal printout (V / I / %Span)
         └─ WebSocket ws://<pi-ip>:8765
              → desktop-app (DCS)
```

Shunt confirmation from terminal: `V≈2.00 @ I≈8.02 mA` ⇒ **R≈250 Ω**.

## Parts / BOM

### On the wood-board assembly

| Part | Role |
|---|---|
| Raspberry Pi 4 Model B | Runs `dcs_server.py` |
| Green GPIO screw-terminal breakout | Wiring from Pi header |
| Green perfboard HAT + standoffs | Carries level shifter / ADC interconnect |
| Blue 4 Bi-Directional Level Shifters | 5 V ADS ↔ 3.3 V Pi I²C |
| ADS1115 @ 5 V | 16-bit ADC |
| 250 Ω ±0.1% shunt | 4–20 mA → 1–5 V |
| Mean Well DIN-rail 24 VDC | Loop supply |
| Brass ground bar + DIN TBs | Star ground / landings |
| Rosemount TT | 4–20 mA process input |
| Fluke 789 | mA OUTPUT checkout |

Amazon reference links (same family as purchased): OONO GPIO TB [B084C69VSQ](https://www.amazon.com/dp/B084C69VSQ), Mean Well HDR-15-24 [B0C9C4LNR4](https://www.amazon.com/dp/B0C9C4LNR4), PT 4-HESI fuse TBs [B0D59WVSKS](https://www.amazon.com/dp/B0D59WVSKS).

Photos: `docs/images/photo_assembled_stack.png`, `photo_fluke_789_8mA.png`, `photo_level_shifter.png`.

## Pinout (copy)

| Pi | Signal | Destination |
|---|---|---|
| Pin 1 (3V3) | LV | Level shifter LV |
| Pin 3 (GPIO2) | SDA | LLC A1 → ADS SDA |
| Pin 5 (GPIO3) | SCL | LLC A2 → ADS SCL |
| Pin 6 (GND) | Ground | LLC/ADS GND + shunt low |
| Pin 11 (GPIO17) | Pump relay (optional) | Relay IN |

ADS1115 **VDD = 5 V**, **ADDR → GND** ⇒ **0x48**. Software PGA ±6.144 V.

## Calibration

- 4 mA → **0 °C** (`DCS_LRV_C`)
- 20 mA → **100 °C** (`DCS_URV_C`)
- Shunt **250 Ω** (`DCS_SHUNT_OHMS`)

## WebSocket note

LAN WebSocket is intentional for remote desktop viewing. If the link drops, the UI is blind until reconnect; the Pi continues sampling and printing locally.

## Safety / grounding

Star the 24 V return with ADC/Pi GND at the **shunt low** / brass bar. Do not inject loop current into the Pi’s 5 V rail except as intentional ADS VDD from a proper 5 V supply.

## Verify

```bash
sudo raspi-config   # Interface Options → I2C → Enable
sudo i2cdetect -y 1 # expect 0x48
cd raspberry-pi
python3 dcs_server.py
# Expect: V=… V  I=… mA  %Span=…%  TT=… °C
```
