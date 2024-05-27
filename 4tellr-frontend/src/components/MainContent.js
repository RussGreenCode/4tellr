// src/components/MainContent.js
import React from 'react';
import ChartComponent from './ChartComponent';
import '../styles/App.css';

const MainContent = ({businessDate}) => {
  return (
    <div className="main-content">
            <ChartComponent businessDate={businessDate} />
    </div>
  );
};

export default MainContent;
