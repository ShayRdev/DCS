import asyncio
import json
import time
from collections import deque

import psutil
import websockets

CONNECTED = set()
LOG_BUFFER = deque(maxlen=200)


async def get_cpu_temp():
    path = "/sys/class/thermal/thermal_zone0/temp"
    try:
        with open(path) as f:
            return float(f.read().strip()) / 1000.0
    except FileNotFoundError:
        return None


async def get_service_state():
    proc = await asyncio.create_subprocess_exec(
        "systemctl",
        "is-active",
        "tankpi.service",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    state = stdout.decode().strip()
    if state not in ("running", "failed", "inactive"):
        state = "inactive"
    return state


async def gather_metrics():
    cpu_pct = psutil.cpu_percent()
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
        "service": {"name": "tankpi.service", "active": service_state},
    }


async def send_all(message: str):
    if CONNECTED:
        await asyncio.gather(
            *[ws.send(message) for ws in list(CONNECTED)], return_exceptions=True
        )


async def metrics_publisher():
    while True:
        data = await gather_metrics()
        await send_all(json.dumps({"type": "metrics", "data": data}))
        await asyncio.sleep(5)


async def temperature_publisher():
    while True:
        temp = await get_cpu_temp()
        if temp is not None:
            await send_all(str(round(temp, 1)))
        await asyncio.sleep(1)


async def init_log_buffer():
    cmd = [
        "journalctl",
        "-u",
        "tankpi.service",
        "-n",
        "200",
        "-o",
        "short-iso",
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    for line in stdout.decode().splitlines():
        LOG_BUFFER.append(line.strip())


async def follow_journal():
    cmd = ["journalctl", "-u", "tankpi.service", "-f", "-o", "short-iso"]
    while True:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        batch = []
        flush_task = None

        async def flush():
            nonlocal batch, flush_task
            if batch:
                await send_all(json.dumps({"type": "log_batch", "lines": batch}))
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
                    flush_task = asyncio.create_task(asyncio.sleep(0.15))
                    flush_task.add_done_callback(lambda t: asyncio.create_task(flush()))
        finally:
            if flush_task is not None:
                await flush()
            try:
                proc.kill()
            except ProcessLookupError:
                pass
            await proc.wait()
        await asyncio.sleep(1)


async def handler(ws):
    CONNECTED.add(ws)
    try:
        # send initial metrics and logs
        data = await gather_metrics()
        await ws.send(json.dumps({"type": "metrics", "data": data}))
        await ws.send(json.dumps({"type": "log_init", "lines": list(LOG_BUFFER)[-200:]}))

        async for message in ws:
            try:
                obj = json.loads(message)
            except json.JSONDecodeError:
                continue
            if obj.get("type") == "ping":
                await ws.send(json.dumps({"type": "pong", "t": obj.get("t")}))
                continue
            if obj.get("command") == "pump":
                state = obj.get("state")
                print(f"Pump command: {state}")
    finally:
        CONNECTED.remove(ws)


async def main():
    await init_log_buffer()
    async with websockets.serve(handler, "", 8765):
        await asyncio.gather(
            metrics_publisher(),
            temperature_publisher(),
            follow_journal(),
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
