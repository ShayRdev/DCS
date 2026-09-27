#!/usr/bin/env python3
"""
DCS Raspberry Pi service

Reads a Rosemount temperature transmitter through an ADS1115 (I²C),
prints live values to the terminal, and streams them to the desktop app
over WebSocket.

Also accepts pump relay commands (GPIO, default BCM 17) — same protocol
used by earlier desktop builds.

Usage (on the Pi):
    cd raspberry-pi
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python3 dcs_server.py

Demo / no-hardware mode:
    python3 dcs_server.py --demo

Environment:
    DCS_WS_HOST=0.0.0.0
    DCS_WS_PORT=8765
    DCS_I2C_BUS=1
    DCS_ADS_ADDR=0x48
    DCS_ADC_CHANNEL=0
    DCS_SHUNT_OHMS=100
    DCS_LRV_C=0
    DCS_URV_C=100
    DCS_PUMP_GPIO=17
    DCS_SAMPLE_HZ=2
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import signal
import sys
import time
from typing import Any, Optional, Set

from rosemount import voltage_to_loop

try:
    import websockets
    from websockets.server import serve
except ImportError:
    print("Install websockets: pip install websockets", file=sys.stderr)
    raise

# Optional GPIO (only on a real Pi with RPi.GPIO)
try:
    import RPi.GPIO as GPIO  # type: ignore

    HAS_GPIO = True
except ImportError:
    HAS_GPIO = False
    GPIO = None  # type: ignore


def env_float(name: str, default: float) -> float:
    return float(os.environ.get(name, default))


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default))
    return int(raw, 0)  # allows 0x48


class PumpRelay:
    def __init__(self, pin: int):
        self.pin = pin
        self.on = False
        if HAS_GPIO:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.output(self.pin, GPIO.HIGH)  # active-low relay boards: HIGH = off

    def set(self, state: bool) -> None:
        self.on = bool(state)
        if HAS_GPIO:
            GPIO.output(self.pin, GPIO.LOW if self.on else GPIO.HIGH)

    def cleanup(self) -> None:
        if HAS_GPIO:
            try:
                GPIO.cleanup(self.pin)
            except Exception:
                pass


class AdcSource:
    """Hardware ADS1115, or a demo waveform when --demo / no bus."""

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self._ads = None
        self._t0 = time.time()
        if not args.demo:
            try:
                from ads1115 import ADS1115

                self._ads = ADS1115(bus=args.i2c_bus, address=args.ads_addr)
                print(
                    f"[adc] ADS1115 on I²C bus {args.i2c_bus} addr 0x{args.ads_addr:02X}",
                    flush=True,
                )
            except Exception as exc:
                print(f"[adc] Hardware open failed ({exc}); falling back to --demo", flush=True)
                self.args.demo = True

    def read_voltage(self) -> float:
        if self._ads is not None:
            return self._ads.read(self.args.channel).voltage_v
        # Demo: ~8–16 mA into 100 Ω → ~0.8–1.6 V (room-temp-ish on 0–100 °C scale)
        t = time.time() - self._t0
        ma = 12.0 + 4.0 * math.sin(t / 6.0)
        return (ma / 1000.0) * self.args.shunt_ohms

    def close(self) -> None:
        if self._ads is not None:
            self._ads.close()


def build_payload(voltage_v: float, args: argparse.Namespace, pump_on: bool) -> dict[str, Any]:
    loop = voltage_to_loop(
        voltage_v,
        shunt_ohms=args.shunt_ohms,
        lrv_c=args.lrv_c,
        urv_c=args.urv_c,
    )
    return {
        "type": "reading",
        "temperature_c": round(loop.temperature_c, 2),
        "voltage_v": round(loop.voltage_v, 4),
        "current_ma": round(loop.current_ma, 3),
        "shunt_ohms": loop.shunt_ohms,
        "lrv_c": loop.lrv_c,
        "urv_c": loop.urv_c,
        "channel": args.channel,
        "pump": "on" if pump_on else "off",
        "ts": time.time(),
    }


async def run_server(args: argparse.Namespace) -> None:
    clients: Set[Any] = set()
    adc = AdcSource(args)
    pump = PumpRelay(args.pump_gpio)
    period = 1.0 / max(args.sample_hz, 0.2)
    stop = asyncio.Event()

    def _stop(*_a: Any) -> None:
        stop.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _stop)
        except NotImplementedError:
            pass

    async def broadcast(text: str) -> None:
        dead = []
        for ws in list(clients):
            try:
                await ws.send(text)
            except Exception:
                dead.append(ws)
        for ws in dead:
            clients.discard(ws)

    async def handler(ws: Any) -> None:
        clients.add(ws)
        peer = getattr(ws, "remote_address", None)
        print(f"[ws] client connected: {peer}", flush=True)
        try:
            async for message in ws:
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    data = {"command": message}
                if data.get("command") == "pump":
                    state = str(data.get("state", "")).lower()
                    pump.set(state in ("on", "1", "true"))
                    print(f"[pump] {'ON' if pump.on else 'OFF'}", flush=True)
                    await broadcast(json.dumps({"type": "pump", "pump": "on" if pump.on else "off"}))
        finally:
            clients.discard(ws)
            print(f"[ws] client disconnected: {peer}", flush=True)

    async def sample_loop() -> None:
        while not stop.is_set():
            try:
                voltage = adc.read_voltage()
                payload = build_payload(voltage, args, pump.on)
                # Terminal readout (what worked on the bench)
                print(
                    f"TT  {payload['temperature_c']:7.2f} °C   "
                    f"I={payload['current_ma']:6.3f} mA   "
                    f"V={payload['voltage_v']:6.4f} V   "
                    f"pump={'ON' if pump.on else 'off'}",
                    flush=True,
                )
                # JSON for the desktop app + plain number for older clients
                await broadcast(json.dumps(payload))
            except Exception as exc:
                print(f"[sample] error: {exc}", flush=True)
            try:
                await asyncio.wait_for(stop.wait(), timeout=period)
            except asyncio.TimeoutError:
                pass

    print(
        f"[*] DCS Pi service  ws://{args.host}:{args.port}  "
        f"shunt={args.shunt_ohms}Ω  LRV={args.lrv_c}°C  URV={args.urv_c}°C  "
        f"demo={args.demo}",
        flush=True,
    )

    async with serve(handler, args.host, args.port):
        sampler = asyncio.create_task(sample_loop())
        await stop.wait()
        sampler.cancel()
        try:
            await sampler
        except asyncio.CancelledError:
            pass

    adc.close()
    pump.cleanup()
    print("[*] stopped", flush=True)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="DCS Raspberry Pi ADS1115 / Rosemount service")
    p.add_argument("--host", default=os.environ.get("DCS_WS_HOST", "0.0.0.0"))
    p.add_argument("--port", type=int, default=env_int("DCS_WS_PORT", 8765))
    p.add_argument("--i2c-bus", type=int, default=env_int("DCS_I2C_BUS", 1))
    p.add_argument("--ads-addr", type=int, default=env_int("DCS_ADS_ADDR", 0x48))
    p.add_argument("--channel", type=int, default=env_int("DCS_ADC_CHANNEL", 0))
    p.add_argument("--shunt-ohms", type=float, default=env_float("DCS_SHUNT_OHMS", 100.0))
    p.add_argument("--lrv-c", type=float, default=env_float("DCS_LRV_C", 0.0))
    p.add_argument("--urv-c", type=float, default=env_float("DCS_URV_C", 100.0))
    p.add_argument("--pump-gpio", type=int, default=env_int("DCS_PUMP_GPIO", 17))
    p.add_argument("--sample-hz", type=float, default=env_float("DCS_SAMPLE_HZ", 2.0))
    p.add_argument("--demo", action="store_true", help="Simulate ADS1115 without hardware")
    return p.parse_args(argv)


def main() -> None:
    args = parse_args()
    asyncio.run(run_server(args))


if __name__ == "__main__":
    main()
