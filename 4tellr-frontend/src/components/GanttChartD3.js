// src/components/GanttChartD3.js
import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';
import { Box, Typography } from '@mui/material';

const GanttChartD3 = ({ data }) => {
  const svgRef = useRef(null);

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous content

    const margin = { top: 20, right: 30, bottom: 30, left: 40 };
    const width = 960 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;

    const chart = svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleTime()
      .domain([d3.min(data, d => new Date(d.start_time)), d3.max(data, d => new Date(d.end_time))])
      .range([0, width]);

    const y = d3.scaleBand()
      .domain(data.map(d => d.event_name))
      .range([0, height])
      .padding(0.1);

    const xAxis = g => g
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x).ticks(width / 80).tickSizeOuter(0));

    const yAxis = g => g
      .call(d3.axisLeft(y).tickSizeOuter(0));

    chart.append('g')
      .call(xAxis);

    chart.append('g')
      .call(yAxis);

    chart.selectAll('.bar')
      .data(data)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(new Date(d.start_time)))
      .attr('y', d => y(d.event_name))
      .attr('width', d => x(new Date(d.end_time)) - x(new Date(d.start_time)))
      .attr('height', y.bandwidth())
      .attr('fill', d => getColorByStatus(d.outcome_status));
  }, [data]);

  const getColorByStatus = (status) => {
    return status === 'NEW' ? 'blue'
      : status === 'ON_TIME' ? 'darkgreen'
      : status === 'MEETS_SLO' ? 'lightgreen'
      : status === 'MEETS_SLA' ? 'orange'
      : status === 'MET_THRESHOLD' ? 'darkgreen'
      : status === 'BREACHED' ? 'red'
      : status === 'NOT_REACHED' ? 'grey'
      : status === 'LATE' ? 'red'
      : 'darkred';
  };

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Process Statistics Gantt Chart
      </Typography>
      <Box style={{ overflowX: 'auto' }}>
        <svg ref={svgRef}></svg>
      </Box>
    </Box>
  );
};

export default GanttChartD3;
