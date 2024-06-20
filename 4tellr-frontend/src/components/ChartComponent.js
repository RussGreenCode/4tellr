import React, { useMemo, useState, useEffect, useContext } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ZAxis, ReferenceLine } from 'recharts';
import { EventsContext } from '../contexts/EventsContext';
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
        <p className="intro">{`Y-Coordinate: ${yCoordinate}`}</p>
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
  const { sortCriterion, selectedTypes, setSelectedEvent, setTabIndex, showLabels } = useContext(EventsContext);
  const [currentTime, setCurrentTime] = useState(Date.now());

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(Date.now());
    }, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  const transformedData = useMemo(() => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      console.error('Invalid data:', data);
      return [];
    }

    const yCoordinateMap = {};
    let yCounter = 0;

    const sortedData = data.flatMap(item => item.data).sort((a, b) => {
      if (sortCriterion === 'EVT') {
        return a.time - b.time;
      } else if (sortCriterion === 'EXP') {
        return (a.expectationTime || a.time) - (b.expectationTime || b.time);
      }
      return 0;
    });

    sortedData.forEach(item => {
      if (!(item.yCoordinate in yCoordinateMap)) {
        yCounter += 1;
        yCoordinateMap[item.yCoordinate] = yCounter;
      }
    });

    return sortedData.map(item => ({
      ...item,
      yValue: yCoordinateMap[item.yCoordinate]
    }));
  }, [data, sortCriterion]);

  const yLabelMap = useMemo(() => {
    const map = {};
    transformedData.forEach(d => {
      map[d.yValue] = d.yCoordinate;
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

  // Convert selectedTypes object to an array of types that are true
  const activeTypes = Object.keys(selectedTypes).filter(type => selectedTypes[type]);

  // Manually set Y-axis ticks
  const yTicks = Array.from(new Set(transformedData.map(item => item.yValue)));

  return (
    <ResponsiveContainer width="100%" height={600}>
      <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: showLabels ? 200 : 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
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
          dataKey="yValue"
          name="Event"
          tickFormatter={showLabels ? formatYAxis : null}
          ticks={yTicks} // Manually set Y-axis ticks
          tick={showLabels ? { fontSize: 12, textAnchor: 'end' } : null}
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
        {activeTypes.map(type => (
          <Scatter
            key={type}
            name={type}
            data={transformedData.filter(d => d.type === type)}
            fill={({ payload }) => payload.color}
            shape={<CustomShape />}
            onClick={(event) => {
              if (event && event.payload) {
                setSelectedEvent(event.payload);
                setTabIndex(1);
              }
            }}
          />
        ))}
        <ReferenceLine x={currentTime} stroke="red" label="Current Time" />
      </ScatterChart>
    </ResponsiveContainer>
  );
};

export default ChartComponent;
