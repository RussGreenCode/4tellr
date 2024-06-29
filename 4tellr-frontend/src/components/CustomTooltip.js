import React from 'react';
import '../styles/AlertArea.css';

const formatTime = (tick) => {
  const totalMinutes = Math.floor(tick / 60);
  const minutes = totalMinutes % 60;
  const hours = Math.floor(totalMinutes / 60);
  return `${hours}:${minutes.toString().padStart(2, '0')}`;
};

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const { eventTime, businessDate } = payload[0].payload;
    return (
      <div className="custom-tooltip">
        <p className="intro">{`Date: ${businessDate}`}</p>
        <p className="intro">{`Time: ${formatTime(eventTime)}`}</p>
      </div>
    );
  }
  return null;
};

export default CustomTooltip;
