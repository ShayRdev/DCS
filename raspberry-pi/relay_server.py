import asyncio
import json

import RPi.GPIO as GPIO
import websockets


GPIO.setmode(GPIO.BCM)


def ensure_pin(pin):
    """Set up a GPIO pin for output if it hasn't been configured."""
    if pin not in ensure_pin.configured:
        GPIO.setup(pin, GPIO.OUT)
        # Most relay boards are active‑low: HIGH = off, LOW = on
        GPIO.output(pin, GPIO.HIGH)
        ensure_pin.configured.add(pin)


ensure_pin.configured = set()


async def handler(websocket):
    async for message in websocket:
        if not message:
            continue
        try:
            data = json.loads(message)
        except Exception:
            data = {'command': message}

        command = data.get('command')
        state = data.get('state')
        pin = int(data.get('gpio', 17))

        if command == 'pump':
            ensure_pin(pin)
            if state == 'on':
                GPIO.output(pin, GPIO.LOW)
            else:
                GPIO.output(pin, GPIO.HIGH)


async def main():
    async with websockets.serve(handler, '0.0.0.0', 8765):
        await asyncio.Future()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    finally:
        GPIO.cleanup()
