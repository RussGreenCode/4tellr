import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const BarChartComponent = ({ data, handleClick }) => (
  <ResponsiveContainer width="100%" height={250}>
    <BarChart
      data={data}
      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
      onClick={(event) => {
        if (event) {
          const { activeLabel } = event;
          const clickedData = data.find(item => item.name === activeLabel);
          handleClick({ eventOutcome: clickedData.eventType});
        }
      }}
    >
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="value">
        {data.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={entry.color} />
        ))}
      </Bar>
    </BarChart>
  </ResponsiveContainer>
);

export default BarChartComponent;
