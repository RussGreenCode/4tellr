// src/components/AlertArea.js
import React from 'react';
import '../styles/App.css';

const AlertArea = () => (
  <div className="alert-area" style={{ backgroundColor: 'var(--alert-background-color)' }}>
    <h5>Alerting Area</h5>
    <p>Metric 1: 100</p>
    <p>Metric 2: 200</p>
    <p>Metric 3: 300</p>
  </div>
);

export default AlertArea;
