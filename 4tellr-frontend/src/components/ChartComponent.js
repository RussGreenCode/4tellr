// src/components/ChartComponent.js
import React, { useMemo } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ZAxis } from 'recharts';
import useEventData from './useEventData';
import '../styles/App.css';

const formatTime = (tick) => {
  const date = new Date(tick);
  return `${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
};

const roundToNearestHour = (timestamp, direction) => {
  const date = new Date(timestamp);
  if (direction === 'start') {
    date.setMinutes(0, 0, 0);
  } else {
    date.setHours(date.getHours() + 1);
    date.setMinutes(0, 0, 0);
  }
  return date.getTime();
};

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const { time, event, size } = payload[0].payload;
    return (
      <div className="custom-tooltip">
        <p className="label">{`Event: ${event}`}</p>
        <p className="intro">{`Time: ${formatTime(time)}`}</p>
      </div>
    );
  }

  return null;
};

const ChartComponent = ({ businessDate }) => {
  const { data, loading, error } = useEventData(businessDate);

  const transformedData = useMemo(() => {
    if (data.length > 0) {
      const sortedData = data[0].data.sort((a, b) => a.primary.getTime() - b.primary.getTime());
      return sortedData.map((d, index) => ({
        time: d.primary.getTime(),
        event: d.secondary,
        size: d.radius,
        yCoordinate: index + 1 // Use an index for the y-axis
      }));
    }
    return [];
  }, [data]);

  const yLabelMap = useMemo(() => {
    const map = {};
    transformedData.forEach((d, index) => {
      map[index + 1] = d.event;
    });
    return map;
  }, [transformedData]);

  const formatYAxis = (tick) => yLabelMap[tick] || tick;

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  const rawDomain = [
    Math.min(...transformedData.map(d => d.time)),
    Math.max(...transformedData.map(d => d.time)),
  ];

  const domain = [
    roundToNearestHour(rawDomain[0], 'start'),
    roundToNearestHour(rawDomain[1], 'end'),
  ];

  const ticks = [];
  for (let tick = domain[0]; tick <= domain[1]; tick += 60 * 60 * 1000) {
    ticks.push(tick);
  }

  return (
    <ResponsiveContainer width="100%" height={500}>
      <ScatterChart
        margin={{ top: 20, right: 20, bottom: 20, left: 100 }} // Increased left margin
      >
        <CartesianGrid />
        <XAxis
          type="number"
          dataKey="time"
          name="Time"
          domain={domain}
          tickFormatter={formatTime}
          ticks={ticks}
        />
        <YAxis
          type="number"
          dataKey="yCoordinate"
          name="Event"
          tickFormatter={formatYAxis}
          tick={{ fontSize: 12, angle: -30, textAnchor: 'end' }} // Rotated labels
        />
        <ZAxis
          type="number"
          dataKey="size"
          range={[10, 100]} // Adjust size range here to make dots smaller
          name="Size"
        />
        <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
        <Legend />
        <Scatter name="Events" data={transformedData} fill="#8884d8" />
      </ScatterChart>
    </ResponsiveContainer>
  );
};

export default ChartComponent;
