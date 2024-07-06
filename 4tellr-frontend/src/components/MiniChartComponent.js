// src/components/MiniChartComponent.js
import React, { useMemo, useState, useEffect, useContext, useRef } from 'react';
import Plot from 'react-plotly.js';
import { EventsContext } from '../contexts/EventsContext';
import { useTheme } from '@mui/material/styles';
import { transformEventsForChart } from '../utils/transformEvents';
import '../styles/Chart.css';



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


const MiniChartComponent = ({ rawData, width, height }) => {
  const { sortCriterion, selectedTypes, setSelectedEvent, setTabIndex, tabIndex, showLabels, isDrawerOpen } = useContext(EventsContext);
  const theme = useTheme(); // Use the theme context
  const [currentTime, setCurrentTime] = useState(Date.now());
  const hoveredPointRef = useRef(null);
  const selectedPointRef = useRef(null); // Ref for selected point

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(Date.now());
    }, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  const transformedData = useMemo(() => {
    const data = transformEventsForChart(rawData);
    if (!data || data.length === 0) {
      console.error('Invalid data:', data);
      return [];
    }

    const yCoordinateMap = {};
    let yCounter = 0;

    const sortedData = data.sort((a, b) => {
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
      yValue: yCoordinateMap[item.yCoordinate],
      markerSymbol: getMarkerSymbol(item.type)
    }));
  }, [rawData, sortCriterion]);

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

  return (
    <div style={{ width, height }}>
      <Plot
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
          margin: { t: 10, l: showLabels ? 200 : 0, r: 30, b: 50 },
          xaxis: {
            range: rawDomain, // Include one day on both sides
            tickformat: '%Y-%m-%d',
            tickvals: ticks,
            ticktext: ticks.map(t => formatTime(t)),
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
              x0: currentTime,
              x1: currentTime,
              y0: Math.min(...yTicks),
              y1: Math.max(...yTicks),
              line: {
                color: 'red',
                width: 2,
                dash: 'dot'
              }
            }
          ]
        }}
        config={{ displayModeBar: false }}
        onClick={handlePointClick}
        onHover={handleHover}
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
};

export default MiniChartComponent;
