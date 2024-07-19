// src/pages/ProcessStatistics.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import GanttChartD3 from '../components/GanttChartD3';
import { Box, Typography } from '@mui/material';

const GanttChart = () => {
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

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Process Statistics Gantt Chart
      </Typography>
      <GanttChartD3 data={processes} />
    </Box>
  );
};

export default GanttChart;
