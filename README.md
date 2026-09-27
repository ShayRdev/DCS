# DCS — Desktop Control System

Personal portfolio project: a **Raspberry Pi** reads a **Rosemount temperature transmitter** through an **ADS1115** (I²C), prints live values in the terminal, and streams them to an **Electron** desktop app over the LAN.

Built and verified on real hardware (Pi + ADS1115 + Rosemount 4–20 mA loop). Anyone with a Pi, breadboard, and the parts below can reproduce it.

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
├── docs/hardware/        # Schematics + pinout + notes
└── README.md
```

---

## Hardware

| Part | Notes |
|---|---|
| Raspberry Pi (any with I²C) | Enable I²C in `raspi-config` |
| [ADS1115](https://www.adafruit.com/product/1085) | Addr `0x48` (ADDR→GND) |
| 100 Ω ±0.1% shunt | 4–20 mA → 0.4–2.0 V |
| 24 VDC supply | Loop power for the transmitter |
| Rosemount temperature transmitter | 2-wire 4–20 mA |
| [Adafruit 757 LLC](https://www.adafruit.com/product/757) | Only if the ADS runs at 5 V |
| Breadboard + cobbler **or** soldered / flex proto PCB | Same netlist |

### Exact pinout

| Pi header | Signal | Goes to |
|---|---|---|
| Pin 1 (3V3) | Power | ADS1115 VDD |
| Pin 3 (GPIO2) | SDA | ADS1115 SDA |
| Pin 5 (GPIO3) | SCL | ADS1115 SCL |
| Pin 6 (GND) | Ground | ADS1115 GND + **shunt low** |
| Pin 11 (GPIO17) | Optional pump relay | Relay IN (active-low) |

**Loop:** `+24 V` → Rosemount `+` → Rosemount `−` → **shunt high** → ADS1115 **AIN0**; **shunt low** → `24 V−` and ADC/Pi GND (single star).

Drawings (title block + revision A):

- [`docs/hardware/schematic-overview.svg`](docs/hardware/schematic-overview.svg) — SCH-DCS-001
- [`docs/hardware/pinout.svg`](docs/hardware/pinout.svg) — SCH-DCS-002
- [`docs/hardware/hardware-notes.md`](docs/hardware/hardware-notes.md)

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
- Keep 24 V loop grounding at the shunt low side; prefer an isolated loop supply.

---

## License

Personal project — no license applied. Use as inspiration; adapt the pinout to your board.
