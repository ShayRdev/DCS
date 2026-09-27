/**
 * Desktop / CI simulator that mimics raspberry-pi/dcs_server.py
 * Protocol: JSON readings on ws://localhost:8765
 *
 *   npm install && npm start
 */
const WebSocket = require('ws');

const PORT = Number(process.env.DCS_WS_PORT || 8765);
const SHUNT = Number(process.env.DCS_SHUNT_OHMS || 100);
const LRV = Number(process.env.DCS_LRV_C || 0);
const URV = Number(process.env.DCS_URV_C || 100);

const wss = new WebSocket.Server({ port: PORT, host: '0.0.0.0' });
console.log(`Simulator (Rosemount/ADS1115 protocol) on ws://localhost:${PORT}`);

let pumpOn = false;
let t0 = Date.now();

function sample() {
  const t = (Date.now() - t0) / 1000;
  const ma = 12 + 4 * Math.sin(t / 6);
  const voltage = (ma / 1000) * SHUNT;
  const frac = (ma - 4) / 16;
  const temperature_c = LRV + frac * (URV - LRV);
  return {
    type: 'reading',
    temperature_c: Number(temperature_c.toFixed(2)),
    voltage_v: Number(voltage.toFixed(4)),
    current_ma: Number(ma.toFixed(3)),
    shunt_ohms: SHUNT,
    lrv_c: LRV,
    urv_c: URV,
    channel: 0,
    pump: pumpOn ? 'on' : 'off',
    ts: Date.now() / 1000,
  };
}

function broadcast(obj) {
  const text = JSON.stringify(obj);
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) client.send(text);
  });
}

wss.on('connection', (ws) => {
  console.log('Client connected');
  ws.on('message', (raw) => {
    let data;
    try {
      data = JSON.parse(String(raw));
    } catch {
      data = { command: String(raw) };
    }
    if (data.command === 'pump') {
      pumpOn = String(data.state).toLowerCase() === 'on';
      console.log('Pump', pumpOn ? 'ON' : 'OFF');
      broadcast({ type: 'pump', pump: pumpOn ? 'on' : 'off' });
    }
  });
  ws.on('close', () => console.log('Client disconnected'));
});

setInterval(() => {
  const payload = sample();
  console.log(
    `TT  ${payload.temperature_c.toFixed(2)} °C   I=${payload.current_ma.toFixed(3)} mA   V=${payload.voltage_v.toFixed(4)} V`
  );
  broadcast(payload);
}, 500);
