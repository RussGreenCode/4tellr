// src/components/ParentComponent.js
import React, { useState } from 'react';
import DateSelect from './DateSelect';
import ChartComponent from './ChartComponent';

const ParentComponent = () => {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  return (
    <div>
      <DateSelect selectedDate={selectedDate} setSelectedDate={setSelectedDate} />
      <ChartComponent businessDate={selectedDate} />
    </div>
  );
};

export default ParentComponent;
