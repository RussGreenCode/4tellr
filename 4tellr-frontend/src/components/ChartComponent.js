import React, { useMemo } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ZAxis } from 'recharts';
import '../styles/Chart.css';

const formatTime = (tick) => {
  const date = new Date(tick);
  return `${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
};

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const { time, event, type } = payload[0].payload;
    return (
      <div className="custom-tooltip">
        <p className="label">{`Type: ${type}`}</p>
        <p className="intro">{`Event: ${event}`}</p>
        <p className="intro">{`Time: ${formatTime(time)}`}</p>
      </div>
    );
  }
  return null;
};

const getColor = (type, outcomeStatus) => {
  if (type === 'EVT') {
    switch (outcomeStatus) {
      case 'NEW': return 'white';
      case 'ON_TIME': return 'lightgreen';
      case 'MEETS_SLO': return 'darkgreen';
      case 'MEETS_SLA': return 'orange';
      default: return 'red';
    }
  } else {
    return type === 'EXP' ? 'green' : (type === 'SLO' ? 'amber' : 'red');
  }
};

const CustomShape = (props) => {
  const { cx, cy, payload } = props;
  let shape;

  switch (payload.type) {
    case 'EVT': shape = <circle cx={cx} cy={cy} r={5} fill={payload.color} />; break;
    case 'EXP': shape = <rect x={cx - 5} y={cy - 5} width={10} height={10} fill={payload.color} />; break;
    case 'SLO': shape = <path d={`M${cx},${cy - 5} L${cx - 5},${cy + 5} L${cx + 5},${cy + 5} Z`} fill={payload.color} />; break;
    case 'SLA': shape = <rect x={cx - 5} y={cy - 5} width={10} height={10} fill={payload.color} transform={`rotate(45, ${cx}, ${cy})`} />; break;
    default: shape = <circle cx={cx} cy={cy} r={5} fill="black" />;
  }

  return shape;
};

const ChartComponent = ({ data }) => {
  const transformedData = useMemo(() => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      console.error('Invalid data:', data);
      return [];
    }
    return data.flatMap(item => item.data);
  }, [data]);

  const yLabelMap = useMemo(() => {
    const map = {};
    transformedData.forEach(d => {
      map[d.yCoordinate] = d.event;
    });
    return map;
  }, [transformedData]);

  const formatYAxis = (tick) => yLabelMap[tick] || tick;

  if (!transformedData.length) {
    return <div>No data available</div>;
  }

  const rawDomain = [
    Math.min(...transformedData.map(d => d.time)),
    Math.max(...transformedData.map(d => d.time)),
  ];

  const domain = [
    Math.floor(rawDomain[0] / (60 * 60 * 1000)) * (60 * 60 * 1000),
    Math.ceil(rawDomain[1] / (60 * 60 * 1000)) * (60 * 60 * 1000),
  ];

  const ticks = [];
  for (let tick = domain[0]; tick <= domain[1]; tick += 60 * 60 * 1000) {
    ticks.push(tick);
  }

  return (
    <ResponsiveContainer width="100%" height={500}>
      <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 100 }}>
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
          type="category"
          dataKey="yCoordinate"
          name="Event"
          tickFormatter={formatYAxis}
          tick={{ fontSize: 12, angle: -30, textAnchor: 'end' }}
        />
        <ZAxis
          type="number"
          dataKey="size"
          range={[10, 100]}
          name="Size"
        />
        <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
        <Legend
          payload={[
            { value: 'Event', type: 'circle', color: 'lightgreen' },
            { value: 'Expectation', type: 'square', color: 'green' },
            { value: 'SLO', type: 'triangle', color: 'amber' },
            { value: 'SLA', type: 'diamond', color: 'red' }
          ]}
        />
        {['EVT', 'EXP', 'SLO', 'SLA'].map(type => (
          <Scatter
            key={type}
            name={type}
            data={transformedData.filter(d => d.type === type)}
            fill={({ payload }) => payload.color}
            shape={<CustomShape />}
          />
        ))}
      </ScatterChart>
    </ResponsiveContainer>
  );
};

export default ChartComponent;