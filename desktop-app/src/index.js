import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './global.css';

const globalStyle = document.createElement('style');
globalStyle.innerHTML = `
  body, html {
    margin: 0;
    padding: 0;
    height: 100%;
    width: 100%;
  }
`;
document.head.appendChild(globalStyle);

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<React.StrictMode><App /></React.StrictMode>);
