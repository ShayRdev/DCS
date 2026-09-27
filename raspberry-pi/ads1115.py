"""
ADS1115 I²C helper for Raspberry Pi.

Default address 0x48 on bus 1 (Pi SDA=GPIO2 / SCL=GPIO3).
Works without Adafruit CircuitPython — uses smbus2 only.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

try:
    from smbus2 import SMBus
except ImportError:  # pragma: no cover - install on the Pi
    SMBus = None  # type: ignore


# Pointer / config bits (ADS1115 datasheet)
_REG_CONV = 0x00
_REG_CFG = 0x01

_OS_SINGLE = 0x8000
_MUX_SINGLE = {
    0: 0x4000,  # AIN0 vs GND
    1: 0x5000,
    2: 0x6000,
    3: 0x7000,
}
# PGA ±4.096 V → 1 LSB = 125 µV
_PGA_4_096 = 0x0200
_MODE_SINGLE = 0x0100
_DR_128SPS = 0x0080
_COMP_QUE_DISABLE = 0x0003

_FS_VOLTS = 4.096
_LSB = _FS_VOLTS / 32768.0


@dataclass
class AdcSample:
    channel: int
    raw: int
    voltage_v: float


class ADS1115:
    def __init__(self, bus: int = 1, address: int = 0x48):
        if SMBus is None:
            raise RuntimeError("smbus2 is required on the Raspberry Pi (pip install smbus2)")
        self.bus_id = bus
        self.address = address
        self._bus = SMBus(bus)

    def close(self) -> None:
        try:
            self._bus.close()
        except Exception:
            pass

    def read(self, channel: int = 0) -> AdcSample:
        if channel not in _MUX_SINGLE:
            raise ValueError("channel must be 0..3")
        cfg = (
            _OS_SINGLE
            | _MUX_SINGLE[channel]
            | _PGA_4_096
            | _MODE_SINGLE
            | _DR_128SPS
            | _COMP_QUE_DISABLE
        )
        self._bus.write_i2c_block_data(
            self.address, _REG_CFG, [(cfg >> 8) & 0xFF, cfg & 0xFF]
        )
        # 128 SPS ≈ 7.8 ms; wait a little longer for conversion
        time.sleep(0.012)
        data = self._bus.read_i2c_block_data(self.address, _REG_CONV, 2)
        raw = (data[0] << 8) | data[1]
        if raw & 0x8000:
            raw -= 0x10000
        return AdcSample(channel=channel, raw=raw, voltage_v=raw * _LSB)
