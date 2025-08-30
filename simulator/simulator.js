const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });
console.log('Simulator running on ws://localhost:8080');

wss.on('connection', function connection(ws) {
  console.log('Client connected');
  setInterval(() => {
    const data = {
      pressure: (Math.random() * 100).toFixed(2),
      level: (Math.random() * 10).toFixed(2),
      temperature: (20 + Math.random() * 10).toFixed(2),
      flow: (Math.random() * 50).toFixed(2),
    };
    ws.send(JSON.stringify(data));
  }, 1000);
});
