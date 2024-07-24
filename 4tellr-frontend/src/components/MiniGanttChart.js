// src/components/MiniGanttChartD3.js
import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';
import { Box } from '@mui/material';
import '../styles/GantChartD3.css';
import { getEventColorByStatus } from '../utils/GetEventColorByStatus';

const MiniGanttChartD3 = ({ data, width = 1200, height = 500, textSize = 12, sloTime = null, slaTime = null }) => {
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
    svg.selectAll('*').remove();

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

    const tooltip = d3.select(tooltipRef.current)
      .style('position', 'absolute')
      .style('visibility', 'hidden')
      .style('background', 'rgba(0, 0, 0, 0.7)')
      .style('color', '#fff')
      .style('padding', '5px')
      .style('border-radius', '5px')
      .style('pointer-events', 'none');

    renderAxes(chart, x, chartWidth, chartHeight);
    renderBars(chart, x, rowHeight, tooltip);
    renderVerticalLine(chart, x, chartHeight);
    renderSloAndSla(chart, x, chartHeight);

  }, [data, width, height, textSize, sloTime, slaTime]);

  const renderAxes = (chart, x, chartWidth, chartHeight) => {
    const xAxisTop = d3.axisTop(x).ticks(chartWidth / 80).tickSizeOuter(0);
    const xAxisBottom = d3.axisBottom(x).ticks(chartWidth / 80).tickSizeOuter(0);

    d3.select(xAxisTopRef.current)
      .attr('width', chartWidth + margin.left + margin.right)
      .call(xAxisTop);

    d3.select(xAxisBottomRef.current)
      .attr('width', chartWidth + margin.left + margin.right)
      .call(xAxisBottom);
  };

  const renderBars = (chart, x, rowHeight, tooltip) => {
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
      .on('mouseover', (event, d) => showTooltip(tooltip, event, d))
      .on('mousemove', (event) => moveTooltip(tooltip, event))
      .on('mouseout', () => hideTooltip(tooltip));

    rows.append('rect')
      .attr('class', 'bar')
      .attr('x', d => d.start_time ? x(new Date(d.start_time)) : 0)
      .attr('y', rowHeight * 0.25)
      .attr('width', d => d.start_time ? x(new Date(d.end_time)) - x(new Date(d.start_time)) : 0)
      .attr('height', rowHeight * 0.5)
      .attr('fill', d => getEventColorByStatus(d.outcome))
      .attr('rx', 5)
      .attr('ry', 5)
      .on('mouseover', (event, d) => d.start_time && showTooltip(tooltip, event, d))
      .on('mousemove', (event) => moveTooltip(tooltip, event))
      .on('mouseout', () => hideTooltip(tooltip));

    rows.append('text')
      .attr('x', -10)
      .attr('y', rowHeight * 0.5)
      .attr('dy', '.35em')
      .attr('class', 'process-text')
      .attr('text-anchor', 'end')
      .attr('fill', d => getEventColorByStatus(d.outcome))
      .style('font-size', `${textSize}px`)
      .text(d => d.event_name);
  };

  const renderVerticalLine = (chart, x, chartHeight) => {
    const currentTime = new Date();
    chart.append('line')
      .attr('x1', x(currentTime))
      .attr('y1', 0)
      .attr('x2', x(currentTime))
      .attr('y2', chartHeight)
      .attr('stroke', 'red')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '4');

    chart.append('text')
      .attr('x', x(currentTime))
      .attr('y', -10)
      .attr('text-anchor', 'middle')
      .attr('fill', 'red')
      .style('font-size', '10px')
      .text(currentTime.toUTCString());
  };

  const renderSloAndSla = (chart, x, chartHeight) => {
    if (sloTime) {
      chart.append('path')
        .attr('d', d3.symbol().type(d3.symbolTriangle).size(100)())
        .attr('transform', `translate(${x(new Date(sloTime))}, ${chartHeight + margin.bottom / 2})`)
        .attr('fill', 'black');
    }

    if (slaTime) {
      chart.append('path')
        .attr('d', d3.symbol().type(d3.symbolDiamond).size(100)())
        .attr('transform', `translate(${x(new Date(slaTime))}, ${chartHeight + margin.bottom / 2})`)
        .attr('fill', 'black');
    }
  };

  const showTooltip = (tooltip, event, data) => {
    tooltip.html(`
      <div><strong>Event Name:</strong> ${data.event_name}</div>
      <div><strong>Business Date:</strong> ${data.business_date}</div>
      <div><strong>Start Time:</strong> ${new Date(data.start_time).toLocaleString()}</div>
      <div><strong>End Time:</strong> ${new Date(data.end_time).toLocaleString()}</div>
      <div><strong>Expected Start:</strong> ${new Date(data.expected_start_time).toLocaleString()}</div>
      <div><strong>Expected End:</strong> ${new Date(data.expected_end_time).toLocaleString()}</div>
      <div><strong>Duration (seconds):</strong> ${data.duration_seconds}</div>
      <div><strong>Status:</strong> ${data.outcome}</div>
    `);
    tooltip.style('visibility', 'visible');
  };

  const moveTooltip = (tooltip, event) => {
    tooltip.style('top', `${event.pageY - 10}px`);
    tooltip.style('left', `${event.pageX + 10}px`);
  };

  const hideTooltip = (tooltip) => {
    tooltip.style('visibility', 'hidden');
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
