// src/components/GanttChartD3.js
import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';
import { Box } from '@mui/material';
import '../styles/GantChartD3.css';

const GanttChartD3 = ({ data }) => {
  const svgRef = useRef(null);
  const xAxisTopRef = useRef(null);
  const xAxisBottomRef = useRef(null);
  const tooltipRef = useRef(null);
  const margin = { top: 20, right: 30, bottom: 30, left: 200 }; // Defined margin here

  useEffect(() => {

    const width = 1200 - margin.left - margin.right;
    const rowHeight = 20;
    const chartHeight = data.length * rowHeight;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous content

    const chart = svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', chartHeight + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleTime()
      .domain([d3.min(data, d => new Date(d.start_time)), d3.max(data, d => new Date(d.end_time))])
      .range([0, width]);

    const xAxisTop = d3.axisTop(x).ticks(width / 80).tickSizeOuter(0);
    const xAxisBottom = d3.axisBottom(x).ticks(width / 80).tickSizeOuter(0);

    d3.select(xAxisTopRef.current)
      .attr('width', width + margin.left + margin.right)
      .call(xAxisTop);

    d3.select(xAxisBottomRef.current)
      .attr('width', width + margin.left + margin.right)
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
      .attr('fill', d => 'lightgrey')
      .on('mouseover', (event, d) => {
        console.log('mouseover event', d);
        tooltip.html(`
          <div><strong>Event Name:</strong> ${d.event_name}</div>
          <div><strong>Business Date:</strong> ${d.business_date}</div>
          <div><strong>Start Time:</strong> ${new Date(d.start_time).toLocaleString()}</div>
          <div><strong>End Time:</strong> ${new Date(d.end_time).toLocaleString()}</div>
          <div><strong>Exp Start:</strong> ${new Date(d.expected_start_time).toLocaleString()}</div>
          <div><strong>Exp End:</strong> ${new Date(d.expected_end_time).toLocaleString()}</div>
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
      .attr('x', d => x(new Date(d.start_time)))
      .attr('y', rowHeight * 0.25)
      .attr('width', d => x(new Date(d.end_time)) - x(new Date(d.start_time)))
      .attr('height', rowHeight * 0.5)
      .attr('fill', d => getColorByStatus(d.outcome))
      .attr('rx', 5) // Rounded corners x-axis radius
      .attr('ry', 5) // Rounded corners y-axis radius
      .on('mouseover', (event, d) => {
        tooltip.html(`
          <div><strong>Event Name:</strong> ${d.event_name}</div>
          <div><strong>Business Date:</strong> ${d.business_date}</div>
          <div><strong>Start Time:</strong> ${new Date(d.start_time).toLocaleString()}</div>
          <div><strong>End Time:</strong> ${new Date(d.end_time).toLocaleString()}</div>
          <div><strong>Exp Start:</strong> ${new Date(d.expected_start_time).toLocaleString()}</div>
          <div><strong>Exp End:</strong> ${new Date(d.expected_end_time).toLocaleString()}</div>
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

    rows.append('text')
      .attr('x', -10)
      .attr('y', rowHeight * 0.5)
      .attr('dy', '.35em')
      .attr('class', 'process-text')
      .attr('text-anchor', 'end')
      .attr('fill', d => getColorByStatus(d.outcome))
      .text(d => d.event_name);

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
          <Box>
              <svg width={1200} height={25}>
                  <g ref={xAxisTopRef} transform={`translate(${margin.left},20)`}></g>
              </svg>
          </Box>
          <Box style={{overflowY: 'auto', height: '500px'}}>
              <svg ref={svgRef}></svg>
          </Box>
          <Box>
              <svg width={1200} height={40}>
                  <g ref={xAxisBottomRef} transform={`translate(${margin.left},10)`}></g>
              </svg>
          </Box>
          <div ref={tooltipRef} className="tooltip"></div>
      </Box>
  );
};

export default GanttChartD3;
