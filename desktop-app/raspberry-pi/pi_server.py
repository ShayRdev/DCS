
import asyncio, json, os, subprocess, time
from collections import deque

import psutil
from websockets.legacy.server import serve  # legacy signature compatible

CLIENTS = set()
LOG_BUF = deque(maxlen=100)
SERVICE_NAME = "tankpi.service"   # change if needed
PORT = 8770

def cpu_temp_c():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return round(int(f.read().strip())/1000, 1)
    except Exception:
        return None

def service_status():
    try:
        out = subprocess.check_output(
            ["systemctl", "is-active", SERVICE_NAME],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        return out or "inactive"
    except Exception:
        return "inactive"

def metrics_snapshot():
    return {
        "cpu_pct": psutil.cpu_percent(interval=None),
        "cpu_temp_c": cpu_temp_c(),
        "mem_pct": psutil.virtual_memory().percent,
        "disk_root_pct": psutil.disk_usage("/").percent,
        "uptime_s": int(time.time() - psutil.boot_time()),
        "service": {"name": SERVICE_NAME, "active": service_status()},
    }

async def broadcast(obj):
    if not CLIENTS: return
    msg = json.dumps(obj)
    dead = []
    for ws in CLIENTS:
        try:
            await ws.send(msg)
        except Exception:
            dead.append(ws)
    for ws in dead:
        CLIENTS.discard(ws)

def seed_logs():
    try:
        out = subprocess.check_output(
            ["journalctl","-u",SERVICE_NAME,"-n","100","-o","short-iso","--no-pager"],
            text=True, stderr=subprocess.DEVNULL
        )
        for line in out.splitlines():
            LOG_BUF.append(line.rstrip())
    except Exception:
        pass

async def follow_journal():
    try:
        proc = await asyncio.create_subprocess_exec(
            "journalctl","-u",SERVICE_NAME,"-f","-o","short-iso",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
    except Exception:
        return
    while True:
        line = await proc.stdout.readline()
        if not line: await asyncio.sleep(0.1); continue
        text = line.decode(errors="replace").rstrip()
        LOG_BUF.append(text)
        await broadcast({"type":"log","line":text})

async def publish_metrics():
    while True:
        await broadcast({"type":"metrics","data":metrics_snapshot()})
        await asyncio.sleep(5)

async def core_handler(ws):
    CLIENTS.add(ws)
    try:
        # send initial payloads
        await ws.send(json.dumps({"type":"log_init","lines":list(LOG_BUF)}))
        await ws.send(json.dumps({"type":"metrics","data":metrics_snapshot()}))
        # optional ping/pong
        async for msg in ws:
            try:
                obj = json.loads(msg)
                if obj.get("type") == "ping":
                    await ws.send(json.dumps({"type":"pong","t":obj.get("t")}))
            except Exception:
                pass
    finally:
        CLIENTS.discard(ws)

async def handler(ws, *maybe_path):
    await core_handler(ws)

async def main():
    seed_logs()
    asyncio.create_task(follow_journal())
    asyncio.create_task(publish_metrics())
    async with serve(handler, "0.0.0.0", PORT):
        print(f"[*] stats/logs WS on ws://0.0.0.0:{PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
