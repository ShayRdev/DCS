import asyncio
import json
import subprocess
import time
from collections import deque

import psutil
import websockets

CLIENTS = set()
LOG_BUFFER = deque(maxlen=100)


def read_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return float(f.read().strip()) / 1000.0
    except Exception:
        return None


def service_status():
    try:
        out = subprocess.check_output(
            ["systemctl", "is-active", "tankpi.service"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        out = "inactive"
    return out or "inactive"


def collect_metrics():
    cpu_pct = psutil.cpu_percent()
    mem_pct = psutil.virtual_memory().percent
    disk_root_pct = psutil.disk_usage("/").percent
    uptime_s = int(time.time() - psutil.boot_time())
    cpu_temp = read_cpu_temp()
    return {
        "cpu_pct": cpu_pct,
        "cpu_temp_c": cpu_temp,
        "mem_pct": mem_pct,
        "disk_root_pct": disk_root_pct,
        "uptime_s": uptime_s,
        "service": {"name": "tankpi.service", "active": service_status()},
    }


async def broadcast(msg):
    if not CLIENTS:
        return
    data = json.dumps(msg)
    to_drop = set()
    for ws in CLIENTS:
        try:
            await ws.send(data)
        except Exception:
            to_drop.add(ws)
    for ws in to_drop:
        CLIENTS.discard(ws)


async def metrics_publisher():
    while True:
        await asyncio.sleep(5)
        await broadcast({"type": "metrics", "data": collect_metrics()})


async def temp_publisher():
    while True:
        t = read_cpu_temp()
        if t is not None:
            await broadcast({"temp": t})
        await asyncio.sleep(2)


async def follow_journal():
    cmd = ["journalctl", "-u", "tankpi.service", "-f", "-o", "short-iso"]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
    except Exception:
        return
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        text = line.decode(errors="ignore").rstrip()
        LOG_BUFFER.append(text)
        await broadcast({"type": "log", "line": text})


def seed_logs():
    cmd = ["journalctl", "-u", "tankpi.service", "-n", "100", "-o", "short-iso"]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return
    for line in out.splitlines()[-100:]:
        LOG_BUFFER.append(line.rstrip())


async def handler(ws):
    CLIENTS.add(ws)
    try:
        await ws.send(json.dumps({"type": "log_init", "lines": list(LOG_BUFFER)}))
        await ws.send(json.dumps({"type": "metrics", "data": collect_metrics()}))
        async for message in ws:
            try:
                data = json.loads(message)
            except Exception:
                continue
            if data.get("command") == "pump":
                state = "on" if data.get("state") == "on" else "off"
                await broadcast({"pump": state})
    finally:
        CLIENTS.discard(ws)


async def main():
    seed_logs()
    asyncio.create_task(metrics_publisher())
    asyncio.create_task(temp_publisher())
    asyncio.create_task(follow_journal())
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
