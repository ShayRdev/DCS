# DCS — Desktop Control System

Personal portfolio project: a **Raspberry Pi** reads a **Rosemount temperature transmitter** through an **ADS1115** (I²C), prints live values in the terminal, and streams them to an **Electron** desktop app over the LAN.

Built and verified on real hardware (Pi + ADS1115 + Rosemount 4–20 mA loop). Anyone with a Pi, breadboard or junction-box parts, and the BOM below can reproduce it.

---

## Desktop app

Live Rosemount TT-103 readout (demo / simulator link) and pump control:

![DCS dashboard — live temperature and terminal readout](docs/images/dcs_dashboard_live.png)

![DCS dashboard — pump running](docs/images/dcs_dashboard_pump_on.png)

---

## What it measured

| Signal | Source | Path |
|---|---|---|
| Process temperature (°C) | Rosemount 2-wire transmitter | 4–20 mA → 100 Ω shunt → ADS1115 AIN0 → Pi |
| Loop current (mA) / shunt voltage (V) | Same ADC sample | Converted in `raspberry-pi/dcs_server.py` |

Default scale: **4 mA → 0 °C**, **20 mA → 100 °C** (match your transmitter’s LRV/URV).

---

## How the Pi and desktop talk

```
[ Rosemount TT ] --4–20 mA--> [ shunt + ADS1115 ]
                                    |
                                  I²C
                                    |
                            [ Raspberry Pi ]
                            dcs_server.py
                               |      |
                          terminal   WebSocket :8765
                                         |
                                   [ Desktop app ]
                                      Electron
```

- **On the Pi:** `python3 dcs_server.py` samples the ADS1115, prints a terminal readout, and serves `ws://0.0.0.0:8765`.
- **On the desktop:** the Electron app connects to `ws://<pi-ip>:8765`, shows TT-103, loop current, shunt voltage, and a scrolling terminal-style log.
- **Without hardware:** run `simulator/` on your laptop — same JSON protocol — and point the app at `ws://127.0.0.1:8765`.

### Why WebSocket

WebSocket is the remote HMI path: view live readings from another machine on the LAN without SSH or a serial cable. The Pi keeps sampling and printing to its own terminal even if the desktop disconnects. If the link drops, the UI goes blind (shows **Pi link lost**) and reconnects with backoff until the service is reachable again. That failure mode is expected for a LAN viewer — not a reason to force serial for remote desktop use.

Payload example:

```json
{
  "type": "reading",
  "temperature_c": 23.5,
  "voltage_v": 0.976,
  "current_ma": 9.76,
  "pump": "off"
}
```

Optional pump commands (GPIO 17 relay): `{"command":"pump","state":"on"}`.

---

## Repository layout

```
DCS/
├── desktop-app/          # Electron + React UI
├── raspberry-pi/         # ADS1115 reader + WebSocket service
├── simulator/            # LAN-free stand-in for the Pi service
├── docs/
│   ├── hardware/         # PDF schematics + notes
│   └── images/           # App screenshots + BOM illustration
└── README.md
```

---

## Parts / BOM

### Amazon (this build)

| Item | ASIN / link | Role |
|---|---|---|
| **OONO Ultra-Small RPi GPIO Terminal Block Breakout** | [B084C69VSQ](https://www.amazon.com/dp/B084C69VSQ) | Screw-terminal HAT on the Pi 40-pin header for field wiring (SDA/SCL/3V3/GND/GPIO17) |
| **Mean Well HDR-15-24** 15 W ultra-slim DIN-rail PSU (24 VDC / 0.63 A) | [B0C9C4LNR4](https://www.amazon.com/dp/B0C9C4LNR4) | Isolated-style 24 V loop supply for the Rosemount transmitter |
| **PT 4-HESI (5×20) fuse terminal blocks** (Phoenix-style, pack) | [B0D59WVSKS](https://www.amazon.com/dp/B0D59WVSKS) | Fused terminal protection on the 4–20 mA / 24 V loop |

### Core sensing stack

| Part | Notes |
|---|---|
| Raspberry Pi (any with I²C) | Enable I²C in `raspi-config` |
| [ADS1115](https://www.adafruit.com/product/1085) | Addr `0x48` (ADDR→GND) |
| 100 Ω ±0.1% shunt | 4–20 mA → 0.4–2.0 V |
| Rosemount temperature transmitter | 2-wire 4–20 mA |
| [Adafruit 757 LLC](https://www.adafruit.com/product/757) | Only if the ADS runs at 5 V |
| Breadboard + jumpers **or** junction box / soldered proto | Same netlist |

### BOM layout illustration

AI-generated composite of the real parts above in a small junction box (not a photograph of the bench):

![Illustration — BOM layout in junction box](docs/images/dcs_bom_junction_box_illustration.png)

*Illustration — BOM layout (not a photograph).*

---

## Hardware wiring

### Exact pinout

| Pi header (via OONO TB) | Signal | Goes to |
|---|---|---|
| Pin 1 (3V3) | Power | ADS1115 VDD |
| Pin 3 (GPIO2) | SDA | ADS1115 SDA |
| Pin 5 (GPIO3) | SCL | ADS1115 SCL |
| Pin 6 (GND) | Ground | ADS1115 GND + **shunt low** |
| Pin 11 (GPIO17) | Optional pump relay | Relay IN (active-low) |

**Loop:** `+24 V` (HDR-15-24, optional fuse TB) → Rosemount `+` → Rosemount `−` → **shunt high** → ADS1115 **AIN0**; **shunt low** → `24 V−` and ADC/Pi GND (single star).

### Schematics (PDF)

GitHub does **not** inline PDF drawings in Markdown image tags — **open the PDF files** in the repo:

- [docs/hardware/schematic-overview.pdf](docs/hardware/schematic-overview.pdf) — **SCH-DCS-001** rev B (system interconnect)
- [docs/hardware/pinout.pdf](docs/hardware/pinout.pdf) — **SCH-DCS-002** rev B (pinout & terminals)
- [docs/hardware/hardware-notes.md](docs/hardware/hardware-notes.md)

### Check the ADC

```bash
sudo raspi-config   # Interface Options → I2C → Enable
sudo apt install i2c-tools
sudo i2cdetect -y 1
# expect device at 0x48
```

---

## Run on the Raspberry Pi

```bash
cd raspberry-pi
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 dcs_server.py
```

You should see a live terminal stream like:

```text
TT   23.41 °C   I= 9.760 mA   V=0.9760 V   pump=off
```

Demo without the ADS1115:

```bash
python3 dcs_server.py --demo
```

Optional systemd unit: `raspberry-pi/dcs.service` (edit paths for your Pi user).

Useful env vars: `DCS_WS_PORT`, `DCS_SHUNT_OHMS`, `DCS_LRV_C`, `DCS_URV_C`, `DCS_ADS_ADDR`, `DCS_ADC_CHANNEL`.

---

## Run the desktop app

```bash
cd desktop-app
npm install
npm start
```

This starts the React dev server and opens Electron. Set the WebSocket URL in the side panel (default `ws://127.0.0.1:8765` on localhost, or your Pi LAN IP).

Web-only (no Electron window):

```bash
npm run start:web
```

Production build:

```bash
npm run build
```

---

## Run the simulator (no Pi)

```bash
cd simulator
npm install
npm start
# ws://127.0.0.1:8765 — same protocol as the Pi service
```

Then start the desktop app and leave the WS URL at `ws://127.0.0.1:8765`.

---

## Notes

- Temperature on TT-103 comes from the Pi/simulator stream. Tank level / flow / pressure remain local process-view animation driven by the pump control (same idea as the original dashboard).
- Keep 24 V loop grounding at the shunt low side; prefer an isolated loop supply (HDR-15-24).

---

## License

Personal project — no license applied. Use as inspiration; adapt the pinout to your board.
