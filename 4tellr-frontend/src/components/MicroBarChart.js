import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';


const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
        return (
            <div style={{ backgroundColor: 'grey', border: '1px solid #ccc', padding: '5px' }}>
                <p>{payload[0].payload.name}: {payload[0].payload.value}</p>
            </div>
        );
    }

    return null;
};

const MicroBarChart = ({ data, handleClick, year, month, day }) => (

  <ResponsiveContainer width="100%" height={100}>
    <BarChart
      data={data}
      margin={{ top: 0, right: 0, left: 0, bottom: 0 }}
      onClick={(event) => {
        if (event) {
          const { activeLabel } = event;
          const clickedData = data.find(item => item.name === activeLabel);
          // Call handleClick with additional date info
          handleClick({ eventOutcome: clickedData.eventType, year, month, day });
        }
      }}
    >
      <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} angle={-45} textAnchor="end" />
      <YAxis hide />
      <Tooltip content={<CustomTooltip />} />
      <Tooltip />
      <Bar dataKey="value">
        {data.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={entry.color} />
        ))}
      </Bar>
    </BarChart>
  </ResponsiveContainer>
);

export default MicroBarChart;
