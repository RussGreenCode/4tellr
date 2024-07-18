import React, { useState, useEffect } from 'react';
import { Box, Typography } from '@mui/material';
import { Chart } from 'react-google-charts';
import axios from 'axios';

const GanttChartPage = () => {
  const [processes, setProcesses] = useState([]);

  useEffect(() => {
    fetchProcessStatistics();
  }, []);

  const fetchProcessStatistics = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/process/get_process_statistics_list');
      if (response.data) {
        setProcesses(response.data);
      } else {
        console.error('Error fetching process statistics:', response.data.error);
      }
    } catch (error) {
      console.error('Error fetching process statistics:', error);
    }
  };

  const getColorByStatus = (status) => {
    let color;
    color = status === 'NEW' ? 'blue'
      : status === 'ON_TIME' ? 'darkgreen'
      : status === 'MEETS_SLO' ? 'lightgreen'
      : status === 'MEETS_SLA' ? 'orange'
      : status === 'MET_THRESHOLD' ? 'darkgreen'
      : status === 'BREACHED' ? 'red'
      : status === 'NOT_REACHED' ? 'grey'
      : status === 'LATE' ? 'red'
      : 'darkred';
    return color;
  };

  const formatGanttData = () => {
    const data = [
      [
        { type: 'string', label: 'Task ID' },
        { type: 'string', label: 'Task Name' },
        { type: 'string', label: 'Resource' },
        { type: 'date', label: 'Start Date' },
        { type: 'date', label: 'End Date' },
        { type: 'number', label: 'Duration' },
        { type: 'number', label: 'Percent Complete' },
        { type: 'string', label: 'Dependencies' },
      ],
    ];

    processes.forEach((process, index) => {
      const color = getColorByStatus(process.outcome);
      data.push([
        process._id,
        process.event_name,
        process.outcome,
        new Date(process.start_time),
        new Date(process.end_time),
        null,
        100,
        null,
      ]);
    });

    return data;
  };

  const chartData = formatGanttData();

  const options = {
    height: 8000,
    gantt: {
      trackHeight: 30,
    },
  };


  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Process Statistics Gantt Chart
      </Typography>
      <Box style={{ overflowX: 'auto' }}>
        <Chart
          chartType="Gantt"
          width="100%"
          height="800px"
          data={chartData}
          options={options}
        />
      </Box>
    </Box>
  );
};

export default GanttChartPage;
