import React, { useMemo, useState, useEffect, useRef } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ZAxis, ReferenceLine } from 'recharts';
import '../styles/Chart.css';

const formatTime = (tick) => {
  const date = new Date(tick);
  return `${date.getUTCHours()}:${date.getUTCMinutes().toString().padStart(2, '0')}`;
};

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const { time, event, type, yCoordinate } = payload[0].payload;
    return (
      <div className="custom-tooltip">
        <p className="label">{`Type: ${type}`}</p>
        <p className="intro">{`Event: ${event}`}</p>
        <p className="intro">{`Y Coordinate: ${yCoordinate}`}</p>
        <p className="intro">{`Time: ${formatTime(time)}`}</p>
      </div>
    );
  }
  return null;
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

const ZoomableScatterChart = ({ data, sortCriterion }) => {
  const [currentTime, setCurrentTime] = useState(Date.now());
  const [zoomDomain, setZoomDomain] = useState([null, null]);

  const chartRef = useRef();

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(Date.now());
    }, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  const handleWheel = (event) => {
    if (event.deltaY < 0) {
      setZoomDomain(([min, max]) => [min, max - 1]);
    } else {
      setZoomDomain(([min, max]) => [min, max + 1]);
    }
  };


  useEffect(() => {
    const chart = chartRef.current;
    if (chart) {
      chart.addEventListener('wheel', handleWheel);
    }
    return () => {
      if (chart) {
        chart.removeEventListener('wheel', handleWheel);
      }
    };
  }, []);

  const transformedData = useMemo(() => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      console.error('Invalid data:', data);
      return [];
    }
    return data.flatMap(item => item.data).sort((a, b) => {
      if (sortCriterion === 'EVT') {
        return a.time - b.time;
      } else if (sortCriterion === 'EXP') {
        return (a.expectationTime || a.time) - (b.expectationTime || b.time);
      }
      return 0;
    });
  }, [data, sortCriterion]);

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

  const domain = zoomDomain[0] === null || zoomDomain[1] === null ? [
    Math.floor(rawDomain[0] / (60 * 60 * 1000)) * (60 * 60 * 1000),
    Math.ceil(rawDomain[1] / (60 * 60 * 1000)) * (60 * 60 * 1000),
  ] : zoomDomain;

  const ticks = [];
  for (let tick = domain[0]; tick <= domain[1]; tick += 60 * 60 * 1000) {
    ticks.push(tick);
  }

  return (
    <ResponsiveContainer width="100%" height={500}>
      <ScatterChart ref={chartRef} margin={{ top: 20, right: 20, bottom: 20, left: 100 }}>
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
        <ReferenceLine x={currentTime} stroke="red" label="Current Time" />
      </ScatterChart>
    </ResponsiveContainer>
  );
};

export default ZoomableScatterChart;
