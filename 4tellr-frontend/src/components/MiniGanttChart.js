// src/components/MiniGanttChartD3.js
import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';
import { Box } from '@mui/material';
import '../styles/GantChartD3.css';

const MiniGanttChartD3 = ({ data, width = 1200, height = 500, textSize = 12 }) => {
  const svgRef = useRef(null);
  const xAxisTopRef = useRef(null);
  const xAxisBottomRef = useRef(null);
  const tooltipRef = useRef(null);
  const margin = { top: 20, right: 30, bottom: 30, left: 200 };

  useEffect(() => {
    const chartWidth = width - margin.left - margin.right;
    const rowHeight = 20;
    const chartHeight = data.length * rowHeight;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous content

    const chart = svg
      .attr('width', chartWidth + margin.left + margin.right)
      .attr('height', chartHeight + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleTime()
      .domain([
        d3.min(data, d => Math.min(new Date(d.start_time || d.expected_start_time), new Date(d.expected_start_time))),
        d3.max(data, d => Math.max(new Date(d.end_time || d.expected_end_time), new Date(d.expected_end_time)))
      ])
      .range([0, chartWidth]);

    const xAxisTop = d3.axisTop(x).ticks(chartWidth / 80).tickSizeOuter(0);
    const xAxisBottom = d3.axisBottom(x).ticks(chartWidth / 80).tickSizeOuter(0);

    d3.select(xAxisTopRef.current)
      .attr('width', chartWidth + margin.left + margin.right)
      .call(xAxisTop);

    d3.select(xAxisBottomRef.current)
      .attr('width', chartWidth + margin.left + margin.right)
      .call(xAxisBottom);

    const tooltip = d3.select(tooltipRef.current)
      .style('position', 'absolute')
      .style('visibility', 'hidden')
      .style('background', 'rgba(0, 0, 0, 0.7)')
      .style('color', '#fff')
      .style('padding', '5px')
      .style('border-radius', '5px')
      .style('pointer-events', 'none');

    const rows = chart.selectAll('.row')
      .data(data)
      .enter()
      .append('g')
      .attr('class', 'row')
      .attr('transform', (d, i) => `translate(0,${i * rowHeight})`);

    rows.append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(new Date(d.expected_start_time)))
      .attr('y', rowHeight * 0.15)
      .attr('width', d => x(new Date(d.expected_end_time)) - x(new Date(d.expected_start_time)))
      .attr('height', rowHeight * 0.7)
      .attr('fill', 'lightgrey')
      .on('mouseover', (event, d) => {
        tooltip.html(`
          <div><strong>Event Name:</strong> ${d.event_name}</div>
          <div><strong>Business Date:</strong> ${d.business_date}</div>
          <div><strong>Start Time:</strong> ${new Date(d.start_time).toLocaleString()}</div>
          <div><strong>End Time:</strong> ${new Date(d.end_time).toLocaleString()}</div>
          <div><strong>Expected Start:</strong> ${new Date(d.expected_start_time).toLocaleString()}</div>
          <div><strong>Expected End:</strong> ${new Date(d.expected_end_time).toLocaleString()}</div>
          <div><strong>Duration (seconds):</strong> ${d.duration_seconds}</div>
          <div><strong>Status:</strong> ${d.outcome}</div>
        `);
        return tooltip.style('visibility', 'visible');
      })
      .on('mousemove', (event) => {
        return tooltip.style('top', (event.pageY - 10) + 'px').style('left', (event.pageX + 10) + 'px');
      })
      .on('mouseout', () => {
        return tooltip.style('visibility', 'hidden');
      });

    rows.append('rect')
      .attr('class', 'bar')
      .attr('x', d => d.start_time ? x(new Date(d.start_time)) : 0)
      .attr('y', rowHeight * 0.25)
      .attr('width', d => d.start_time ? x(new Date(d.end_time)) - x(new Date(d.start_time)) : 0)
      .attr('height', rowHeight * 0.5)
      .attr('fill', d => getColorByStatus(d.outcome))
      .attr('rx', 5) // Rounded corners x-axis radius
      .attr('ry', 5) // Rounded corners y-axis radius
      .on('mouseover', (event, d) => {
        if (d.start_time) {
          tooltip.html(`
            <div><strong>Event Name:</strong> ${d.event_name}</div>
            <div><strong>Business Date:</strong> ${d.business_date}</div>
            <div><strong>Start Time:</strong> ${new Date(d.start_time).toLocaleString()}</div>
            <div><strong>End Time:</strong> ${new Date(d.end_time).toLocaleString()}</div>
            <div><strong>Expected Start:</strong> ${new Date(d.expected_start_time).toLocaleString()}</div>
            <div><strong>Expected End:</strong> ${new Date(d.expected_end_time).toLocaleString()}</div>
            <div><strong>Duration (seconds):</strong> ${d.duration_seconds}</div>
            <div><strong>Status:</strong> ${d.outcome}</div>
          `);
          return tooltip.style('visibility', 'visible');
        }
      })
      .on('mousemove', (event) => {
        return tooltip.style('top', (event.pageY - 10) + 'px').style('left', (event.pageX + 10) + 'px');
      })
      .on('mouseout', () => {
        return tooltip.style('visibility', 'hidden');
      });

    rows.append('text')
      .attr('x', -10)
      .attr('y', rowHeight * 0.5)
      .attr('dy', '.35em')
      .attr('class', 'process-text')
      .attr('text-anchor', 'end')
      .attr('fill', d => getColorByStatus(d.outcome))
      .style('font-size', `${textSize}px`)
      .text(d => d.event_name);

    // Add vertical line
    const currentTime = new Date();
    chart.append('line')
      .attr('x1', x(currentTime))
      .attr('y1', 0)
      .attr('x2', x(currentTime))
      .attr('y2', chartHeight)
      .attr('stroke', 'red')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '4');

    // Add text above the vertical line
    chart.append('text')
      .attr('x', x(currentTime))
      .attr('y', -10)
      .attr('text-anchor', 'middle')
      .attr('fill', 'red')
      .style('font-size', '10px')
      .text(currentTime.toUTCString());

  }, [data, width, height, textSize]);

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
      <Box>
        <svg width={width} height={25}>
          <g ref={xAxisTopRef} transform={`translate(${margin.left},20)`}></g>
        </svg>
      </Box>
      <Box style={{ overflowY: 'auto', height: height }}>
        <svg ref={svgRef}></svg>
      </Box>
      <Box>
        <svg width={width} height={40}>
          <g ref={xAxisBottomRef} transform={`translate(${margin.left},10)`}></g>
        </svg>
      </Box>
      <div ref={tooltipRef} className="tooltip"></div>
    </Box>
  );
};

export default MiniGanttChartD3;
