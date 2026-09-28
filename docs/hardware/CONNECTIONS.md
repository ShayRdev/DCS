# DCS — Wire-level connections (SKiDL / KiCad input)

**Revision:** D · **Date:** 2026-09-28  
**Audience:** Downstream schematic generation (SKiDL / KiCad). This file is the **netlist truth** in Markdown. Prefer this over PDF drawings for automated schematic build.

**Project one-liner:** Raspberry Pi 4 reads a Rosemount 2-wire 4–20 mA temperature transmitter through a **250 Ω** shunt into an **ADS1115** (5 V), with I²C crossing a blue **4 Bi-Directional Level Shifters** module on a green perfboard HAT; `dcs_server.py` prints `V` / `I` / `%Span` and serves WebSocket `:8765` to the desktop app.

**Sources (confirmed):** `raspberry-pi/ads1115.py`, `raspberry-pi/dcs_server.py`, `raspberry-pi/rosemount.py`, `docs/hardware/hardware-notes.md`, `README.md`, bench photos under `docs/images/` and `/cursor/stores/self/media/bench/`.

**Non-goals**
- WebSocket / Electron UI are **software-only** — do **not** draw them as electrical nets.
- No Serial Dynamics (or other company) branding on the schematic.
- Do **not** invent footprints, MPN, or pin numbers marked `TODO / unverified`.

---

## 1. Voltage rails

| Rail net | Nominal | Source | Used by |
|---|---|---|---|
| `+24V_LOOP` | 24 VDC | Mean Well DIN-rail PSU output `+V` (HDR-15-24 family) | Rosemount loop supply + |
| `0V_LOOP` | 24 V return | Mean Well `−V` | Loop return; **starred** with signal GND at shunt-low / brass bar |
| `+5V_ADS` | 5 VDC | **Pi 5 V header** (physical pin 2 or 4) → LLC `HV` and ADS1115 `VDD` — *see TODO if a separate 5 V regulator was used* | ADS1115 VDD, LLC HV |
| `+3V3_PI` | 3.3 VDC | Pi header pin 1 (`3V3`) | LLC `LV` |
| `GND` | 0 V signal / star | Pi GND + brass ground bar + ADS GND + LLC GND + shunt low | Common reference |

**Star ground rule (confirmed intent):** Tie `0V_LOOP`, ADS `GND`, LLC `GND`, and Pi `GND` at a **single star** near **shunt low** / brass DIN ground bar. Do not float the loop return relative to the ADC.

---

## 2. Block list (named nets between blocks)

```
[AC mains] --L/N/PE--> [PSU_MW Mean Well] --+24V_LOOP / 0V_LOOP--> [loop]

[TT_RM Rosemount 2-wire]
    LOOP+ <--+24V_LOOP
    LOOP- --> NET_LOOP_RETURN --> [RS250 shunt high] --> NET_SHUNT_HIGH --> [U_ADS AIN0]
                              --> [RS250 shunt low]  --> GND (star)

[U_PI Raspberry Pi 4]
    3V3  --> +3V3_PI --> [U_LLC LV]
    5V   --> +5V_ADS --> [U_LLC HV] and [U_ADS VDD]
    GND  --> GND
    GPIO2/SDA --> I2C_SDA_3V3 --> [U_LLC A1]
    GPIO3/SCL --> I2C_SCL_3V3 --> [U_LLC A2]
    GPIO17 (optional) --> RELAY_DRV --> [K_RELAY]   # software default; may be unwired on bench

[U_LLC 4 Bi-Directional Level Shifters]
    B1 --> I2C_SDA_5V --> [U_ADS SDA]
    B2 --> I2C_SCL_5V --> [U_ADS SCL]
    GND --> GND

[U_ADS ADS1115]
    ADDR --> GND          # ⇒ I²C address 0x48
    AIN0 --> NET_SHUNT_HIGH
    GND  --> GND
```

**Physical carriers (not separate electrical blocks, but required for layout):**
- `J_GPIO` — green GPIO screw-terminal breakout on Pi 40-pin header (OONO-style / equiv.)
- `PCB_PERF` — green perfboard HAT on standoffs; hosts `U_LLC` (soldered) and jumpers to ADS / shunt sense
- `DIN` — aluminum DIN rail: `PSU_MW`, brass ground bar, black DIN terminal blocks

---

## 3. Master connection table

Columns: **From** → **To**, **Net**, **Notes**.  
Ref designators are logical (`U_PI`, `U_LLC`, …), not KiCad library IDs.

### 3.1 Power — Mean Well → loop

| From | To | Net | Notes |
|---|---|---|---|
| AC L (mains) | `PSU_MW` AC L / Line input | `AC_L` | Photo: black/white into Mean Well top terminals — exact silkscreen labels `TODO / unverified` |
| AC N (mains) | `PSU_MW` AC N / Neutral | `AC_N` | Same |
| PE / green earth (if present) | Brass ground bar | `PE` | Photo shows green wire to brass bar |
| `PSU_MW` `+V` | Rosemount `+` (LOOP+) **or** DIN TB → Rosemount `+` | `+24V_LOOP` | 24 VDC loop supply |
| `PSU_MW` `−V` | Brass bar / DIN TB → shunt low / star | `0V_LOOP` ≡ `GND` at star | Must meet shunt low |

### 3.2 4–20 mA process loop + 250 Ω shunt

| From | To | Net | Notes |
|---|---|---|---|
| `+24V_LOOP` | `TT_RM` transmitter `+` | `+24V_LOOP` | 2-wire Rosemount |
| `TT_RM` transmitter `−` | **Shunt high** (`RS250` pad A) | `NET_LOOP_RETURN` | Series in loop return |
| `RS250` pad A (high) | `U_ADS` `AIN0` | `NET_SHUNT_HIGH` | Sense voltage; **this is “shunt high”** |
| `RS250` pad B (low) | `GND` star (brass bar + ADS GND + Pi GND) | `GND` | **“Shunt low”** |
| `RS250` | — | — | **250 Ω ±0.1%** (documented). Bench: `V≈2.00` @ `I≈8.02 mA` ⇒ R≈250 Ω. **Not 100 Ω.** |

**Loop current path (series):**  
`PSU +V` → `TT_RM +` → `TT_RM −` → **shunt** → `PSU −V` / star GND.

**Voltage measured by ADC:** across shunt = `I_loop × 250 Ω` → `AIN0` vs `GND`.

### 3.3 Raspberry Pi 4 ↔ level shifter ↔ ADS1115 (I²C)

| From | To | Net | Notes |
|---|---|---|---|
| `U_PI` header **pin 1** `3V3` | `U_LLC` `LV` | `+3V3_PI` | Confirmed in hardware-notes |
| `U_PI` header **pin 2 or 4** `5V` | `U_LLC` `HV` **and** `U_ADS` `VDD` | `+5V_ADS` | ADS runs at **5 V**; exact which 5V pin jumpered on perfboard: `TODO / unverified` (either Pi 5V pin is electrically fine) |
| `U_PI` header **pin 6** `GND` (or any Pi GND) | `U_LLC` `GND` (both LV- and HV-side GND pins on module) | `GND` | Module has GND on both edges — bond both to star |
| `U_PI` header **pin 3** `GPIO2` / `SDA` | `U_LLC` `A1` | `I2C_SDA_3V3` | BCM numbering; I²C bus **1** |
| `U_PI` header **pin 5** `GPIO3` / `SCL` | `U_LLC` `A2` | `I2C_SCL_3V3` | |
| `U_LLC` `B1` | `U_ADS` `SDA` | `I2C_SDA_5V` | HV side |
| `U_LLC` `B2` | `U_ADS` `SCL` | `I2C_SCL_5V` | HV side |
| `U_ADS` `ADDR` | `GND` | `GND` | ⇒ I²C address **0x48** (`ads1115.py`, `DCS_ADS_ADDR`) |
| `U_ADS` `GND` | `GND` | `GND` | |
| `U_ADS` `AIN0` | `NET_SHUNT_HIGH` | `NET_SHUNT_HIGH` | Channel **0** (`DCS_ADC_CHANNEL=0`) |
| `U_LLC` `A3`,`A4`,`B3`,`B4` | — | — | **Unused** on documented build. Optionally NC or tie unused to GND — `TODO / unverified` whether tied on bench |
| `U_ADS` `AIN1`,`AIN2`,`AIN3` | — | — | Unused. Optional tie to `GND` — `TODO / unverified` |

### 3.4 Optional pump relay (software-supported, may be unwired)

| From | To | Net | Notes |
|---|---|---|---|
| `U_PI` header **pin 11** `GPIO17` | Relay module `IN` | `RELAY_DRV` | `dcs_server.py` default `DCS_PUMP_GPIO=17`; active-low drive assumed for common relay boards |
| Relay coil / contact supply | — | — | **Not confirmed on wood-board photo** — mark entire relay path optional / `TODO / unverified` if drawing permanent field IO |

### 3.5 GPIO screw TB + perfboard HAT (physical path)

Logical nets above are carried as:

| Logical net | Physical path |
|---|---|
| Pi GPIO / 3V3 / 5V / GND | Pi 40-pin → **green screw-terminal breakout** (`J_GPIO`) → Dupont / hookup wire |
| I²C 3V3 side | Wires from `J_GPIO` SDA/SCL/3V3/GND → **green perfboard HAT** pads → soldered into `U_LLC` LV / A1 / A2 / GND |
| I²C 5V side | Perfboard traces/jumpers `U_LLC` B1/B2/HV → `U_ADS` SDA/SCL/VDD |
| Shunt sense | Twisted or short leads from shunt high → ADS `AIN0`; shunt low → star / brass bar |

Exact perfboard hole coordinates / which ADS breakout footprint: **`TODO / unverified`** (hand-wired).

---

## 4. Per-device pin tables (confirmed only)

### 4.1 `U_PI` — Raspberry Pi 4 Model B (40-pin header, BCM)

| Physical pin | Name | Direction | Net | Confirmed? |
|---|---|---|---|---|
| 1 | `3V3` | Power out | `+3V3_PI` | Yes → LLC `LV` |
| 2 | `5V` | Power out | `+5V_ADS` (candidate) | Yes as rail source; which of pin 2 vs 4 used: TODO |
| 4 | `5V` | Power out | `+5V_ADS` (candidate) | Same |
| 3 | `GPIO2` / `SDA` | I²C | `I2C_SDA_3V3` | Yes |
| 5 | `GPIO3` / `SCL` | I²C | `I2C_SCL_3V3` | Yes |
| 6 | `GND` | Power | `GND` | Yes (any GND pin OK) |
| 9, 14, 20, 25, 30, 34, 39 | `GND` | Power | `GND` | Available; unused unless jumpered |
| 11 | `GPIO17` | Out | `RELAY_DRV` | Software yes; hardware optional |
| Others | — | — | — | Not used by this design |

**Code:** I²C bus `1`, address `0x48`, channel `0` — `dcs_server.py` / `ads1115.py`.

### 4.2 `U_LLC` — Blue “4 Bi-Directional Level Shifters” module

Photo silkscreen (confirmed):

| Side | Pins (top→bottom as labeled) |
|---|---|
| LV edge | `LV`, `A1`, `A2`, `A3`, `A4`, `GND` |
| HV edge | `HV`, `B1`, `B2`, `B3`, `B4`, `GND` |

| Pin | Net | Mate | Confirmed? |
|---|---|---|---|
| `LV` | `+3V3_PI` | Pi pin 1 | Yes |
| `HV` | `+5V_ADS` | Pi 5V / ADS VDD | Yes (rail) |
| `GND` (LV) | `GND` | Star | Yes |
| `GND` (HV) | `GND` | Star | Yes — bond both GND pads |
| `A1` | `I2C_SDA_3V3` | Pi GPIO2 | Yes (docs map A1=SDA) |
| `A2` | `I2C_SCL_3V3` | Pi GPIO3 | Yes (docs map A2=SCL) |
| `B1` | `I2C_SDA_5V` | ADS `SDA` | Yes |
| `B2` | `I2C_SCL_5V` | ADS `SCL` | Yes |
| `A3`,`A4`,`B3`,`B4` | — | — | Unused / TODO |

**Do not invent** MOSFET MPN or module Amazon ASIN unless later confirmed — treat as generic 4-ch MOSFET LLC (Adafruit 757–class).

### 4.3 `U_ADS` — ADS1115 breakout

| Pin | Net | Notes | Confirmed? |
|---|---|---|---|
| `VDD` | `+5V_ADS` | **5 V**, not 3V3 | Yes |
| `GND` | `GND` | | Yes |
| `SCL` | `I2C_SCL_5V` | Via LLC B2 | Yes |
| `SDA` | `I2C_SDA_5V` | Via LLC B1 | Yes |
| `ADDR` | `GND` | Address **0x48** | Yes |
| `AIN0` | `NET_SHUNT_HIGH` | Single-ended vs GND | Yes |
| `AIN1`–`AIN3` | — | Unused | Optional GND |
| `ALERT/RDY` | — | Not used in software | Leave NC |

**Software config (`ads1115.py`):**
- Mux: AIN0 vs GND (`channel=0`)
- PGA: **±6.144 V** (`_PGA_6_144`, full-scale 6.144 V) — covers 1–5 V shunt span
- Mode: single-shot; data rate 128 SPS
- LSB: `6.144 / 32768` V

**Footprint / breakout MPN:** Adafruit 1085–class or equiv. Exact board silkscreen on bench: `TODO / unverified`.

### 4.4 `RS250` — shunt resistor

| Pad | Net | Notes |
|---|---|---|
| High | `NET_SHUNT_HIGH` | To ADS `AIN0` and to Rosemount `−` / loop return into shunt |
| Low | `GND` | Star with `0V_LOOP` |

| Spec | Value | Source |
|---|---|---|
| Resistance | **250 Ω** | Terminal math + docs (default `DCS_SHUNT_OHMS=250`) |
| Tolerance | ±0.1% | Documented target |
| Power | ≥ (0.02 A)² × 250 ≈ 0.1 W → use ≥¼ W | Derived |

### 4.5 `PSU_MW` — Mean Well DIN-rail 24 V (HDR-15-24 family)

| Terminal | Net | Confirmed? |
|---|---|---|
| AC inputs | `AC_L` / `AC_N` | Yes functionally; label text on photo TODO |
| `+V` | `+24V_LOOP` | Yes |
| `−V` | `0V_LOOP` → star `GND` | Yes |
| ASIN reference | [B0C9C4LNR4](https://www.amazon.com/dp/B0C9C4LNR4) | README BOM |

Exact model faceplate on the wood board may be HDR vs DR series — treat as **24 V DIN Mean Well**; MPN faceplate: `TODO / unverified` if not HDR-15-24.

### 4.6 `TT_RM` — Rosemount 2-wire temperature transmitter

| Terminal | Net | Notes |
|---|---|---|
| `+` | `+24V_LOOP` | Loop-powered |
| `−` | Into shunt high / `NET_LOOP_RETURN` | 4–20 mA |

Exact Rosemount model (e.g. 3144P vs other): **portfolio “Rosemount-style”** — exact MPN `TODO / unverified` unless engraved in a photo (not required for nets).

### 4.7 Brass ground bar + DIN TBs

| Item | Role |
|---|---|
| Brass bar on green DIN mounts | PE + star `GND` landing |
| Black DIN terminal blocks | Land `+24V_LOOP`, loop return, field pairs |

Individual TB numbering: `TODO / unverified`.

### 4.8 Fluke 789 — **test only, not permanent circuit**

| Role | Connection during checkout |
|---|---|
| mA OUTPUT source | Substitutes for / injects into loop to verify shunt + ADC (photo: **8.000 mA**, **25.0%** OUTPUT) |
| Permanent schematic | **Omit** from production netlist; optional dashed “test fixture” block only |

---

## 5. Calibration & terminal stream (software ↔ hardware)

**Ohm’s law / span (confirmed):**

\[
V = I \times R,\quad R = 250\ \Omega
\]

| \(I\) (mA) | \(V\) (V) | %Span | Default TT (°C) if LRV=0, URV=100 |
|---|---|---|---|
| 4.00 | 1.000 | 0% | 0.00 |
| 8.00 | 2.000 | 25% | 25.00 |
| 12.00 | 3.000 | 50% | 50.00 |
| 16.00 | 4.000 | 75% | 75.00 |
| 20.00 | 5.000 | 100% | 100.00 |

\[
\%\mathrm{Span} = (I_{\mathrm{mA}} - 4) / 16 \times 100
\]

\[
T = \mathrm{LRV} + \frac{I_{\mathrm{mA}} - 4}{16}(\mathrm{URV} - \mathrm{LRV})
\]

**Terminal line format** (`dcs_server.py`):

```text
V=2.000 V  I=8.00 mA  %Span=25.0%  TT=25.00 °C  pump=off
```

Bench Mac capture matched `V=… V  I=… mA  %Span=…%` at ~25 / 50 / 75% points.

---

## 6. BOM (parts actually used / documented)

| Ref | Description | Link / note |
|---|---|---|
| `U_PI` | Raspberry Pi 4 Model B | Bench photos |
| `J_GPIO` | Ultra-small RPi GPIO terminal block breakout (OONO) | [Amazon B084C69VSQ](https://www.amazon.com/dp/B084C69VSQ) |
| `PCB_PERF` | Green perfboard HAT + standoffs | Hand-assembled |
| `U_LLC` | Blue 4 Bi-Directional Level Shifters module | Photo silkscreen; Adafruit 757–class |
| `U_ADS` | ADS1115 breakout @ 5 V, ADDR→GND = 0x48 | [Adafruit 1085](https://www.adafruit.com/product/1085) or equiv. |
| `RS250` | 250 Ω ±0.1% shunt | **Not 100 Ω** |
| `PSU_MW` | Mean Well DIN 24 VDC ~15 W | [Amazon B0C9C4LNR4](https://www.amazon.com/dp/B0C9C4LNR4) HDR-15-24 |
| DIN fuse TB (optional) | PT 4-HESI (5×20) style | [Amazon B0D59WVSKS](https://www.amazon.com/dp/B0D59WVSKS) |
| — | Brass ground bar + DIN TBs | On rail |
| `TT_RM` | Rosemount 2-wire 4–20 mA TT | Field instrument |
| — | Fluke 789 ProcessMeter | Test only |
| — | Hookup wire / DIN jumpers | As needed |

---

## 7. Net name checklist (for SKiDL)

Must exist as named nets:

- `+24V_LOOP`, `0V_LOOP` (bonded to `GND` at star)
- `+5V_ADS`, `+3V3_PI`, `GND`
- `I2C_SDA_3V3`, `I2C_SCL_3V3`, `I2C_SDA_5V`, `I2C_SCL_5V`
- `NET_SHUNT_HIGH` (AIN0 / shunt high / Rosemount − into shunt)
- `RELAY_DRV` (optional)

**Key nets to get right first:**  
`I2C_SDA_3V3`/`I2C_SCL_3V3` (Pi GPIO2/3) ↔ LLC ↔ `I2C_SDA_5V`/`I2C_SCL_5V` (ADS); **`NET_SHUNT_HIGH`** = shunt high → ADS `AIN0`; shunt low → `GND` star; shunt = **250 Ω**.

---

## 8. Explicit TODOs / unverified (do not invent)

| Item | Status |
|---|---|
| Exact Mean Well faceplate MPN on wood board | TODO / unverified (family: 24 V DIN) |
| Which Pi 5V pin (2 vs 4) feeds `+5V_ADS` | TODO / unverified |
| ADS1115 breakout brand silkscreen | TODO / unverified |
| Whether AIN1–3 and LLC A3/A4/B3/B4 tied to GND | TODO / unverified |
| Perfboard hole map / jumper colors per net | TODO / unverified |
| Pump relay hardware present on bench | Optional / likely unwired |
| Rosemount exact model number | TODO / unverified |
| Fuse TB in series with loop on final build | Optional (Amazon part documented) |

---

## 9. Software-only (do not schematic)

- `dcs_server.py` WebSocket `ws://0.0.0.0:8765`
- Electron / React desktop app
- Simulator (`simulator/simulator.js`)

---

## 10. Quick ASCII interconnect (summary)

```
          +24V_LOOP
             |
          [TT_RM]
             |
        NET_LOOP_RETURN
             |
        (shunt high)----+---- NET_SHUNT_HIGH ----> U_ADS.AIN0
             |          |
           [RS250]      |
             |          |
        (shunt low)-----+---- GND star <---- U_ADS.GND, U_LLC.GND, U_PI.GND, PSU−
             |
          0V_LOOP

U_PI.3V3 ----> U_LLC.LV
U_PI.5V  ----> U_LLC.HV + U_ADS.VDD
U_PI.SDA ----> U_LLC.A1 ----> U_LLC.B1 ----> U_ADS.SDA
U_PI.SCL ----> U_LLC.A2 ----> U_LLC.B2 ----> U_ADS.SCL
U_ADS.ADDR --> GND   (0x48)
```
