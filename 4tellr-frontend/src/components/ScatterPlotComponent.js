import React, { useEffect, useRef } from 'react';
import Plot from 'react-plotly.js';
import { useTheme } from '@mui/material/styles';
import * as d3 from 'd3';

// Function to calculate the best fit line
const calculateBestFitLine = (data) => {
  const x = data.map(d => d.businessDate);
  const y = data.map(d => d.eventTime);

  const n = x.length;
  const sumX = d3.sum(x);
  const sumY = d3.sum(y);
  const sumXY = d3.sum(x.map((xi, i) => xi * y[i]));
  const sumXX = d3.sum(x.map(xi => xi * xi));

  const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
  const intercept = (sumY - slope * sumX) / n;

  const fitLine = x.map(xi => slope * xi + intercept);

  return { x, fitLine, slope, intercept };
};

// Function to get the color based on outcome status
const getColor = (event) => {
  return event.outcomeStatus === 'NEW' ? 'blue'
       : event.outcomeStatus === 'ON_TIME' ? 'darkgreen'
       : event.outcomeStatus === 'MEETS_SLO' ? 'lightgreen'
       : event.outcomeStatus === 'MEETS_SLA' ? 'orange'
       : event.outcomeStatus === 'MET_THRESHOLD' ? 'darkgreen'
       : event.outcomeStatus === 'BREACHED' ? 'red'
       : event.outcomeStatus === 'NOT_REACHED' ? 'grey'
       : event.outcomeStatus === 'LATE' ? 'red'
       : 'darkred';  // Default color
};

// Function to format event time as HH:MM
const formatTime = (tick) => {
  const totalMinutes = Math.floor(tick / 60);
  const minutes = totalMinutes % 60;
  const hours = Math.floor(totalMinutes / 60);
  return `${hours}:${minutes.toString().padStart(2, '0')}`;
};

// Function to generate regular time intervals
const generateRegularTimeIntervals = (minTime, maxTime, maxTicks) => {
  const range = maxTime - minTime;
  const interval = Math.ceil(range / (maxTicks - 1) / 60) * 60; // interval in seconds
  const intervals = [];

  // Adjust minTime and maxTime to ensure the first and last ticks are below and above the actual data range
  const adjustedMinTime = Math.floor(minTime / interval) * interval;
  const adjustedMaxTime = Math.ceil(maxTime / interval) * interval;

  for (let time = adjustedMinTime; time <= adjustedMaxTime; time += interval) {
    intervals.push(time);
  }
  return intervals;
};

const ScatterPlotComponent = ({ data }) => {
  const plotRef = useRef(null);
  const theme = useTheme(); // Use the theme context

  const { x, fitLine, slope, intercept } = calculateBestFitLine(data);

  // Determine the min and max event times
  const minEventTime = Math.min(...data.map(d => d.eventTime));
  const maxEventTime = Math.max(...data.map(d => d.eventTime));

  // Generate regular time intervals with a maximum of 10 ticks
  const regularTimeIntervals = generateRegularTimeIntervals(minEventTime, maxEventTime, 10);

  // Determine the min and max business dates and add one day on both sides
  const minDate = new Date(Math.min(...data.map(d => new Date(d.businessDate))));
  const maxDate = new Date(Math.max(...data.map(d => new Date(d.businessDate))));
  const adjustedMinDate = new Date(minDate);
  adjustedMinDate.setDate(minDate.getDate() - 1);
  const adjustedMaxDate = new Date(maxDate);
  adjustedMaxDate.setDate(maxDate.getDate() + 1);

  useEffect(() => {
    // Plotly react-plotly.js will automatically handle the rendering
  }, [data]);

  return (
    <div>
      <Plot
        data={[
          {
            x: data.map(d => new Date(d.businessDate)),
            y: data.map(d => d.eventTime),
            mode: 'markers',
            type: 'scatter',
            marker: {
              color: data.map(d => getColor(d)),
              size: 10 // Set the desired size of the scatter points here
            },
            name: 'Event Times'
          },
          {
            x: data.map(d => new Date(d.businessDate)),
            y: fitLine,
            mode: 'lines',
            type: 'scatter',
            line: { color: 'red' },
            name: 'Best Fit Line'
          }
        ]}
        layout={{
          margin: { t: 10, l: 50, r: 30, b: 50 }, // Adjust the margin to reduce white space
          xaxis: {
            title: 'Business Date',
            range: [adjustedMinDate, adjustedMaxDate], // Set the range to include one more day on both sides
            tickformat: '%Y-%m-%d',
            tickvals: data.map(d => new Date(d.businessDate)),
            ticktext: data.map(d => new Date(d.businessDate).toISOString().split('T')[0]),
            titlefont: {
              color: theme.palette.text.primary
            },
            tickfont: {
              color: theme.palette.text.primary
            },
            gridcolor: theme.palette.divider
          },
          yaxis: {
            title: 'Event Time',
            tickvals: regularTimeIntervals,
            ticktext: regularTimeIntervals.map(t => formatTime(t)),
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
          width: 1200, // Set the desired width here
          height: 400 // Set the desired height here
        }}
        config={{
          displayModeBar: true // Always show the mode bar
        }}
        ref={plotRef}
      />
      <style jsx>{`
        .modebar-container {
          position: absolute !important;
          top: 10px;
          right: 0px;
        }
      `}</style>
    </div>
  );
};

export default ScatterPlotComponent;
