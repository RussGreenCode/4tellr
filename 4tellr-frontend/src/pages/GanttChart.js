// src/pages/ProcessStatistics.js
import React, {useState, useEffect, useContext} from 'react';
import axios from 'axios';
import GanttChartD3 from '../components/GanttChartD3';
import { Box, Typography } from '@mui/material';
import {EventsContext} from "../contexts/EventsContext";
import config from '../config';

const GanttChart = () => {
  const { businessDate } = useContext(EventsContext);
  const [processes, setProcesses] = useState([]);


  useEffect(() => {
    const fetchProcessStatistics = async () => {
      try {
        const response = await axios.get(`${config.baseUrl}/api/process/get_process_statistics_list`, {
          params: { business_date: businessDate }
        });

        if (response.data) {
          setProcesses(response.data);
        } else {
          console.error('Error fetching process statistics:', response.data.error);
        }
      } catch (error) {
        console.error('Error fetching process statistics:', error);
      }
    };

    fetchProcessStatistics();
  }, [businessDate]);

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
