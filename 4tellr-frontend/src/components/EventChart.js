import React from 'react';
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, LineChart, Line
} from 'recharts';
import { Bubble } from 'react-chartjs-2';
import { VictoryChart, VictoryScatter, VictoryAxis, VictoryTooltip } from 'victory';

const mockData = [
  { time: new Date('2024-05-24T09:00:00').getTime(), event: 'Meeting 1', color: '#8884d8', size: 100 },
  { time: new Date('2024-05-24T10:00:00').getTime(), event: 'Meeting 2', color: '#82ca9d', size: 200 },
  { time: new Date('2024-05-24T11:00:00').getTime(), event: 'Meeting 3', color: '#ffc658', size: 150 },
  { time: new Date('2024-05-24T12:00:00').getTime(), event: 'Meeting 4', color: '#d84f31', size: 180 },
  { time: new Date('2024-05-24T13:00:00').getTime(), event: 'Meeting 5', color: '#d831b8', size: 120 },
  { time: new Date('2024-05-24T14:00:00').getTime(), event: 'Meeting 6', color: '#31d8ca', size: 220 },
  { time: new Date('2024-05-24T15:00:00').getTime(), event: 'Meeting 7', color: '#d8d631', size: 90 },
  { time: new Date('2024-05-24T16:00:00').getTime(), event: 'Meeting 8', color: '#f5a91b', size: 130 },
  { time: new Date('2024-05-24T17:00:00').getTime(), event: 'Meeting 9', color: '#8a1bf5', size: 140 },
  { time: new Date('2024-05-24T18:00:00').getTime(), event: 'Meeting 10', color: '#1bf548', size: 110 },
];

const formatTime = (tick) => {
  const date = new Date(tick);
  return `${date.getHours()}:${date.getMinutes()}`;
};

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const { time, event } = payload[0].payload;
    return (
      <div className="custom-tooltip">
        <p className="label">{`Event: ${event}`}</p>
        <p className="intro">{`Time: ${formatTime(time)}`}</p>
      </div>
    );
  }

  return null;
};

const EventChart = () => {
  const data = mockData.map((d) => ({
    x: d.time,
    y: d.event,
    r: d.size,
    color: d.color,
  }));

  // Option 1: Scatter Chart (Recharts)
  const ScatterRecharts = () => (
    <ResponsiveContainer width="100%" height={300}>
      <ScatterChart
        margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
      >
        <CartesianGrid />
        <XAxis
          type="number"
          dataKey="time"
          name="Time"
          domain={['dataMin', 'dataMax']}
          tickFormatter={formatTime}
        />
        <YAxis
          type="category"
          dataKey="event"
          name="Event"
        />
        <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
        <Legend />
        <Scatter name="Events" data={mockData} fill="#8884d8">
          {mockData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Scatter>
      </ScatterChart>
    </ResponsiveContainer>
  );

  // Option 2: Line Chart (Recharts)
  const LineRecharts = () => (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart
        data={mockData}
        margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          type="number"
          dataKey="time"
          name="Time"
          domain={['dataMin', 'dataMax']}
          tickFormatter={formatTime}
        />
        <YAxis
          type="category"
          dataKey="event"
          name="Event"
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Line type="monotone" dataKey="event" stroke="#8884d8" />
      </LineChart>
    </ResponsiveContainer>
  );


  // Option 4: Scatter Chart (Victory)
  const ScatterVictory = () => (
    <VictoryChart domainPadding={20}>
      <VictoryAxis
        tickFormat={(tick) => formatTime(tick)}
      />
      <VictoryAxis dependentAxis />
      <VictoryScatter
        data={data}
        x="x"
        y="y"
        labels={({ datum }) => datum.y}
        style={{ data: { fill: ({ datum }) => datum.color } }}
        labelComponent={<VictoryTooltip />}
      />
    </VictoryChart>
  );

  // Option 5: Bubble Chart (Chart.js)

  return (
    <div>
      <h2>Scatter Chart (Recharts)</h2>
      <ScatterRecharts />
      <h2>Line Chart (Recharts)</h2>
      <LineRecharts />
      <h2>Scatter Chart (Victory)</h2>
      <ScatterVictory />
    </div>
  );
};

export default EventChart;
