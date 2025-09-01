#!/usr/bin/env python3
"""
pi_server.py - metrics and log WebSocket server for TankPi.

Setup:
    pip install websockets psutil

Run:
    python3 pi_server.py

Optional systemd unit (/etc/systemd/system/pi_stats.service):
    [Unit]
    Description=TankPi stats server
    After=network.target

    [Service]
    ExecStart=/usr/bin/python3 /home/pi/tankpi/pi_server.py
    Restart=always

    [Install]
    WantedBy=multi-user.target

Diagnostics:
    # If "address already in use"
    sudo lsof -i :8770 -P -n
    sudo fuser -k 8770/tcp

Verify:
    websocat -t ws://<pi>:8770
    # Expect: log_init, metrics, log_batch ...
"""

import asyncio
import json
import time
from collections import deque
from typing import Deque, Set, Optional, List

import psutil
import websockets

# ---- Config ----
PORT = 8770
SERVICE = "tankpi.service"
LOG_MAX = 200
LOG_BATCH_MS = 50
METRICS_PERIOD = 5

# ---- State ----
CONNECTED: Set[websockets.WebSocketServerProtocol] = set()
LOG_BUFFER: Deque[str] = deque(maxlen=LOG_MAX)
FOLLOW_TASK: Optional[asyncio.Task] = None


# ---- Helpers ----
async def get_cpu_temp() -> Optional[float]:
    path = "/sys/class/thermal/thermal_zone0/temp"
    try:
        with open(path) as f:
            return float(f.read().strip()) / 1000.0
    except FileNotFoundError:
        return None


async def get_service_state() -> str:
    proc = await asyncio.create_subprocess_exec(
        "systemctl",
        "is-active",
        SERVICE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    state = stdout.decode().strip()
    if state not in ("running", "failed", "inactive"):
        state = "inactive"
    return state


async def gather_metrics() -> dict:
    cpu_pct = psutil.cpu_percent(interval=None)
    cpu_temp_c = await get_cpu_temp()
    mem_pct = psutil.virtual_memory().percent
    disk_root_pct = psutil.disk_usage("/").percent
    uptime_s = int(time.time() - psutil.boot_time())
    service_state = await get_service_state()
    return {
        "cpu_pct": cpu_pct,
        "cpu_temp_c": cpu_temp_c,
        "mem_pct": mem_pct,
        "disk_root_pct": disk_root_pct,
        "uptime_s": uptime_s,
        "service": {"name": SERVICE, "active": service_state},
    }


# ---- Broadcast ----
async def broadcast(message: str) -> None:
    if not CONNECTED:
        return
    webs = list(CONNECTED)
    results = await asyncio.gather(*(ws.send(message) for ws in webs), return_exceptions=True)
    for ws, res in zip(webs, results):
        if isinstance(res, Exception):
            CONNECTED.discard(ws)


# ---- Publishers ----
async def metrics_publisher() -> None:
    while True:
        data = await gather_metrics()
        await broadcast(json.dumps({"type": "metrics", "data": data}))
        await asyncio.sleep(METRICS_PERIOD)


async def init_log_buffer() -> None:
    cmd = [
        "journalctl",
        "-u",
        SERVICE,
        "-n",
        str(LOG_MAX),
        "-o",
        "short-iso",
        "--no-pager",
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    for line in stdout.decode().splitlines():
        LOG_BUFFER.append(line.strip())


async def follow_journal() -> None:
    while True:
        cmd = [
            "journalctl",
            "-u",
            SERVICE,
            "-f",
            "-o",
            "short-iso",
            "--no-pager",
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        batch: List[str] = []
        flush_task: Optional[asyncio.Task] = None

        async def flush() -> None:
            nonlocal batch, flush_task
            if batch:
                await broadcast(json.dumps({"type": "log_batch", "lines": batch}))
                batch = []
            flush_task = None

        try:
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                text = line.decode().rstrip()
                LOG_BUFFER.append(text)
                batch.append(text)
                if flush_task is None:
                    flush_task = asyncio.create_task(asyncio.sleep(LOG_BATCH_MS / 1000.0))
                    flush_task.add_done_callback(lambda t: asyncio.create_task(flush()))
        except asyncio.CancelledError:
            if flush_task is not None:
                flush_task.cancel()
            try:
                proc.kill()
            except ProcessLookupError:
                pass
            await proc.wait()
            raise
        finally:
            if flush_task is not None:
                await flush()
            try:
                proc.kill()
            except ProcessLookupError:
                pass
            await proc.wait()
        await asyncio.sleep(1)


# ---- WS Handler & Main ----
async def handler(ws: websockets.WebSocketServerProtocol) -> None:
    CONNECTED.add(ws)
    try:
        data = await gather_metrics()
        await ws.send(json.dumps({"type": "metrics", "data": data}))
        await ws.send(json.dumps({"type": "log_init", "lines": list(LOG_BUFFER)}))
        async for message in ws:
            try:
                obj = json.loads(message)
            except json.JSONDecodeError:
                continue
            if obj.get("type") == "ping":
                await ws.send(json.dumps({"type": "pong", "t": obj.get("t")}))
    finally:
        CONNECTED.discard(ws)


async def main() -> None:
    await init_log_buffer()
    async with websockets.serve(handler, "0.0.0.0", PORT):
        print(f"Listening on ws://0.0.0.0:{PORT}")
        metrics_task = asyncio.create_task(metrics_publisher())
        global FOLLOW_TASK
        FOLLOW_TASK = asyncio.create_task(follow_journal())
        try:
            await asyncio.Future()
        finally:
            metrics_task.cancel()
            if FOLLOW_TASK is not None:
                FOLLOW_TASK.cancel()
                await asyncio.gather(FOLLOW_TASK, return_exceptions=True)
            await asyncio.gather(metrics_task, return_exceptions=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
