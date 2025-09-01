import React, { useEffect, useState } from 'react';
import Tank from './components/Tank';
import Pipe from './components/Pipe';
import PumpButton from './components/PumpButton';
import Navbar from './components/Navbar';
import TransmitterWithGauge from './components/TransmitterWithGauge';
import LogViewer from './components/LogViewer';

function Dashboard() {
  const [data, setData] = useState({
    pressure: 0,
    level: 0,
    temperature: 0,
    flow: 0,
    pumpStatus: false
  });
  const [logs, setLogs] = useState([]);

  const tapHeightPercent = 20;
  const visualMinFill = 8;

  useEffect(() => {
    const ws = new WebSocket('ws://192.168.1.125:8765');
    ws.onopen = () => console.log("Connected to Raspberry Pi simulator");
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'log')
          setLogs(prev => [...prev, msg.line].slice(-200));
        else if (msg.type === 'log_init')
          setLogs(msg.lines.slice(-200));
      } catch (e) {
        const temp = parseInt(event.data);
        setData(prev => ({ ...prev, temperature: temp }));
      }
    };
    ws.onclose = () => console.log("Disconnected from simulator");
    return () => ws.close();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setData(prev => {
        let { level, flow, temperature, pressure, pumpStatus } = prev;
        if (pumpStatus) {
          flow = 50;
          level = Math.min(level + 0.1, 100);
          temperature = Math.min(temperature + 0.05, 80);
          pressure = 15;
        } else {
          flow = 0;
          level = Math.max(level - 0.05, 0);
          pressure = 0;
        }
        return { ...prev, flow, level, temperature, pressure };
      });
    }, 500);
    return () => clearInterval(interval);
  }, []);

  const togglePump = () => setData(prev => ({ ...prev, pumpStatus: !prev.pumpStatus }));

  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    background: '#0a0a0a',
    minHeight: '100vh',
    fontFamily: 'Orbitron, Helvetica Neue, sans-serif',
    padding: '20px',
    paddingTop: '50px',
    color: '#0ff'
  };

  const ltLevel = data.level < tapHeightPercent ? 0 : ((data.level - tapHeightPercent) * 27.68 / 100).toFixed(1);
  const tankVisualLevel = Math.max(data.level, visualMinFill);

  return (
    <div style={containerStyle}>
      <Navbar temperature={35} humidity={62} site="Unit 400 Tank Control" />
      <PumpButton pumpStatus={data.pumpStatus} togglePump={togglePump} />

      <svg width="1300" height="700" style={{ backgroundColor: '#000', borderRadius: '8px' }}>
        {/* Process pipes */}
        <Pipe x1={200} y1={530} x2={280} y2={530} color="#0ff" glow />
        <Pipe x1={280} y1={530} x2={280} y2={600} color="#0ff" glow />
        <Pipe x1={280} y1={600} x2={320} y2={600} color="#0ff" glow />

        <Pipe x1={246} y1={400} x2={350} y2={400} color="#00f" glow />
        <Pipe x1={350} y1={400} x2={350} y2={450} color="#00f" glow />
        <Pipe x1={350} y1={450} x2={500} y2={450} color="#f00" glow />

        {/* Tank */}
        <foreignObject x="50" y="130" width="160" height="470">
          <Tank tag="T-G-122" level={tankVisualLevel} />
        </foreignObject>

        {/* Transmitters with new futuristic UI */}
        <foreignObject x="550" y="150" width="400" height="120">
          <TransmitterWithGauge tag="PT-102" value={data.pressure} unit="psi" min={0} max={30} />
        </foreignObject>

        <foreignObject x="550" y="280" width="400" height="120">
          <TransmitterWithGauge tag="TT-103" value={data.temperature.toFixed(1)} unit="°C" min={0} max={100} />
        </foreignObject>

        <foreignObject x="550" y="410" width="400" height="120">
          <TransmitterWithGauge tag="FT-104" value={data.flow} unit="gpm" min={0} max={100} />
        </foreignObject>

        <foreignObject x="320" y="550" width="400" height="120">
          <TransmitterWithGauge tag="LT-101" value={ltLevel} unit="inH₂O" min={0} max={30} />
        </foreignObject>
      </svg>
      <div style={{ width: '100%', marginTop: '20px' }}>
        <LogViewer lines={logs} />
      </div>
    </div>
  );
}

export default Dashboard;
