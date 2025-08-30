import React from 'react';
import ReactDOM from 'react-dom';
import Dashboard from './Dashboard';
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

ReactDOM.render(<Dashboard />, document.getElementById('root'));
