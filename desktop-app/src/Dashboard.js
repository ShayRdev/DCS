import React, { useEffect, useState } from 'react';
import Tank from './components/Tank';
import Transmitter from './components/Transmitter';
import Pipe from './components/Pipe';
import PumpButton from './components/PumpButton';

function Dashboard() {
  const [data, setData] = useState({
    pressure: 0,
    level: 0,
    temperature: 0,
    flow: 0,
    pumpStatus: false
  });

  useEffect(() => {
    const ws = new WebSocket('ws://192.168.1.125:8765');
    ws.onopen = () => console.log("Connected to Raspberry Pi simulator");
    ws.onmessage = (event) => {
      const temp = parseInt(event.data);
      setData(prev => ({ ...prev, temperature: temp }));
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
    backgroundColor: '#1e1e1e',
    minHeight: '100vh',
    fontFamily: 'sans-serif',
    padding: '20px',
    color: '#fff'
  };

  return (
    <div style={containerStyle}>
      <PumpButton pumpStatus={data.pumpStatus} togglePump={togglePump} />

      <div style={{ display: 'flex', position: 'relative', alignItems: 'center' }}>
        <Tank tag="T-G-122" level={data.level} />

        {/* Pipes */}
        <Pipe top="200px" left="180px" width="100px" height="5px" />
        <Pipe top="200px" left="280px" width="5px" height="100px" />

        {/* Transmitters */}
        <div style={{ position: 'absolute', left: '-120px', top: '400px' }}>
          <Transmitter tag="LT-101" value={(data.level * 27.68 / 100).toFixed(1)} unit="inH₂O" />
        </div>
        <div style={{ position: 'absolute', left: '320px', top: '120px' }}>
          <Transmitter tag="PT-102" value={data.pressure} unit="psi" />
        </div>
        <div style={{ position: 'absolute', left: '320px', top: '220px' }}>
          <Transmitter tag="TT-103" value={data.temperature.toFixed(1)} unit="°C" />
        </div>
        <div style={{ position: 'absolute', left: '320px', top: '320px' }}>
          <Transmitter tag="FT-104" value={data.flow} unit="gpm" />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
