# DCS — Desktop Control System

A personal hardware-software project that bridges a custom-modified Raspberry Pi with a desktop app, enabling full two-way communication: send commands, read sensor data, and monitor your hardware in real time.

---

## Overview

DCS consists of two parts:

- **`desktop-app/`** — An Electron/JavaScript desktop application that acts as a dashboard, configuration tool, and command interface for the Pi.
- **`simulator/`** — A software simulator for testing the system without needing the physical hardware connected.

The system communicates with a custom-built Raspberry Pi breakout setup, designed and hand-soldered with the following hardware:

| Component | Purpose |
|---|---|
| **ADS1115** | 16-bit analog-to-digital converter — reads analog sensor values over I²C |
| **Adafruit 757 Logic Level Converter (4CH)** | Safely bridges 3.3V (Pi GPIO) and 5V signals from external components |

---

## Architecture

```
[ Desktop App ]
      |
   TCP/Serial/WebSocket
      |
[ Raspberry Pi ]
      |
  I²C / GPIO
      |
[ ADS1115 ] ──── Analog sensors
[ Logic Level Converter ] ──── 5V peripherals
```

---

## Features

- 📡 **Real-time data** — Reads and displays live sensor values from the ADS1115 ADC
- 🎛️ **Send commands** — Control outputs and settings on the Pi from the desktop
- 📊 **Dashboard** — Visual monitor for system state
- ⚙️ **Configuration** — Adjust parameters without touching the Pi directly
- 🧪 **Simulator** — Test and develop without physical hardware

---

## Hardware Requirements

- Raspberry Pi (any model with GPIO + I²C support)
- [ADS1115 16-bit ADC](https://www.adafruit.com/product/1085) — wired to I²C (SDA/SCL)
- [Adafruit 757 4-Channel Logic Level Converter](https://www.adafruit.com/product/757)
- Custom breakout board (hand-soldered)

### Pi Setup

Enable I²C on the Raspberry Pi:

```bash
sudo raspi-config
# Interface Options → I2C → Enable
```

Verify the ADS1115 is detected:

```bash
sudo i2cdetect -y 1
# Should show device at address 0x48 (default)
```

---

## Getting Started

### Desktop App

```bash
cd desktop-app
npm install
npm start
```

### Simulator

```bash
cd simulator
npm install
npm start
```

---

## Project Structure

```
DCS/
├── desktop-app/     # Electron desktop application
│   └── ...
├── simulator/       # Software simulator for offline development
│   └── ...
└── README.md
```

---

## Notes

This is a personal project built for my own hardware setup. The custom breakout board and wiring are specific to my configuration — your pinout and I²C addresses may differ. Feel free to adapt it to your own Pi setup.

---

## License

Personal project — no license applied. Feel free to use as inspiration.
