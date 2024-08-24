import React, { useMemo, useState, useEffect, useContext, useRef } from 'react';
import Plot from 'react-plotly.js';
import { EventsContext } from '../contexts/EventsContext';
import { useTheme } from '@mui/material/styles';
import '../styles/Chart.css';
import { ResponsiveContainer } from "recharts";
import { generateYCoordinateIndexMap } from '../utils/GenerateYCoordinateIndexMap';

const formatTime = (tick) => {
  const date = new Date(tick);
  return `${date.getUTCHours()}:${date.getUTCMinutes().toString().padStart(2, '0')}`;
};

// Define marker symbols based on the type
const getMarkerSymbol = (type) => {
  switch (type) {
    case 'EVT': return 'circle';
    case 'EXP': return 'square';
    case 'SLO': return 'triangle-up';
    case 'SLA': return 'diamond';
    default: return 'circle';
  }
};

const ChartComponent = ({ data }) => {
  const theme = useTheme(); // Use the theme context
  const { sortCriterion, selectedTypes, setSelectedEvent, setTabIndex, tabIndex, showLabels, isDrawerOpen, setSelectedEventList } = useContext(EventsContext);
  const [currentTime, setCurrentTime] = useState(new Date().toISOString());
  const hoveredPointRef = useRef(null);
  const selectedPointRef = useRef(null); // Ref for selected point

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(Date.now());
    }, 6000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  const yCoordinateMap = generateYCoordinateIndexMap(data)

  const transformedData = useMemo(() => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      console.error('Invalid data:', data);
      return [];
    }

    return data.flatMap(item => item.data).map(item => ({
      ...item,
      yValue: sortCriterion === 'EXP' ? yCoordinateMap[item.yCoordinate].exp_index : yCoordinateMap[item.yCoordinate].evt_index,
      markerSymbol: getMarkerSymbol(item.type)
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

  const adjustedDomain = (() => {
    const times = transformedData.map(d => d.time);
    const minTime = Math.min(...times);
    const maxTime = Math.max(...times);
    const timeDifference = maxTime - minTime;
    const adjustment = timeDifference * 0.02;
    return [
      minTime - adjustment, // Reduce min time by 5% of the time difference
      maxTime + adjustment  // Increase max time by 5% of the time difference
    ];
  })();

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

  let yTicks = Array.from(new Set(transformedData.map(item => item.yValue)));
  if (yTicks.length > 20) {
    const interval = Math.ceil(yTicks.length / 20);
    yTicks = yTicks.filter((_, index) => index % interval === 0);
  }

  const handlePointClick = (event) => {
    if (event.points.length > 0) {
      selectedPointRef.current = event.points[0].customdata;
      setSelectedEvent(selectedPointRef.current);
      if (tabIndex === 0) setTabIndex(1);
    }
  };

  const handleHover = (event) => {
    if (event.points.length > 0) {
      hoveredPointRef.current = event.points[0].customdata;
    } else {
      hoveredPointRef.current = null;
    }
  };

  const handleRelayout = (event) => {
    if (event['xaxis.range[0]'] && event['xaxis.range[1]']) {
      const xRange = [event['xaxis.range[0]'], event['xaxis.range[1]']];
      const yRange = [event['yaxis.range[0]'], event['yaxis.range[1]']];

      const selectedPoints = transformedData.filter(d =>
        d.time >= new Date(xRange[0]).getTime() &&
        d.time <= new Date(xRange[1]).getTime() &&
        d.yValue >= yRange[0] &&
        d.yValue <= yRange[1]
      );

      const selectedEventList = selectedPoints.map(d => ({
        event: d.event,
        status: d.status
      }));

      setSelectedEventList(selectedEventList);
    }
  };

  return (
    <ResponsiveContainer width="100%" height={600}>
      <Plot
        key={isDrawerOpen}
        data={activeTypes.map(type => ({
          x: transformedData.filter(d => d.type === type).map(d => d.time),
          y: transformedData.filter(d => d.type === type).map(d => d.yValue),
          text: transformedData.filter(d => d.type === type).map(d => `Event: ${d.event}<br>Time: ${formatTime(d.time)}<br>Type: ${d.type}<br>Y-Coordinate: ${d.yCoordinate}`),
          mode: 'markers',
          type: 'scatter',
          marker: {
            symbol: transformedData.filter(d => d.type === type).map(d => d.markerSymbol),
            color: transformedData.filter(d => d.type === type).map(d => d.color),
            size: 10
          },
          name: type,
          customdata: transformedData.filter(d => d.type === type)
        }))}
        layout={{
          margin: { t: 10, l: showLabels ? 200 : 0, r: 0,  b: 50 },
          xaxis: {
            range: adjustedDomain, // Include one day on both sides
            tickformat: '%Y-%m-%d',
            tickvals: ticks,
            ticktext: ticks.map(t => formatTime(t)),
            title: 'Time',
            titlefont: {
              color: theme.palette.text.primary
            },
            tickfont: {
              color: theme.palette.text.primary
            },
            gridcolor: theme.palette.divider
          },
          yaxis: {
            tickvals: yTicks,
            ticktext: yTicks.map(t => formatYAxis(t)),
            titlefont: {
              color: theme.palette.text.primary
            },
            tickfont: {
              color: theme.palette.text.primary
            },
            gridcolor: theme.palette.divider
          },
          paper_bgcolor: theme.palette.background.default,
          plot_bgcolor: theme.palette.background.default,
          showlegend: false,
          shapes: [
            {
              type: 'line',
              x0: new Date(currentTime).getTime(),
              x1: new Date(currentTime).getTime(),
              y0: Math.min(...yTicks),
              y1: Math.max(...yTicks),
              line: {
                color: 'red',
                width: 2,
                dash: 'dot'
              }
            }
          ],
          annotations: [
            {
              x: new Date(currentTime).getTime(),
              y: Math.max(...yTicks),
              text: formatTime(new Date(currentTime).getTime()),
              showarrow: false,
              xanchor: 'left',
              yanchor: 'bottom',
              font: {
                color: theme.palette.text.primary
              },
              bgcolor: theme.palette.background.default
            }
          ]
        }}
        config={{ displayModeBar: true }}
        onClick={handlePointClick}
        onHover={handleHover}
        onRelayout={handleRelayout}
        style={{ width: '100%', height: '600px' }}
      />
    </ResponsiveContainer>
  );
};

export default ChartComponent;
