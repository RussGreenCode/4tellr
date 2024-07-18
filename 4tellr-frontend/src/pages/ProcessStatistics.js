import React, { useState, useEffect } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableHead, TableRow, TableSortLabel } from '@mui/material';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const ProcessStatistics = () => {
  const [processes, setProcesses] = useState([]);
  const [order, setOrder] = useState('asc');
  const [orderBy, setOrderBy] = useState('duration_seconds');

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


  const handleSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const sortedProcesses = processes.sort((a, b) => {
    if (orderBy === 'duration_seconds') {
      return order === 'asc' ? a.duration_seconds - b.duration_seconds : b.duration_seconds - a.duration_seconds;
    }
    return 0;
  });

  const chartData = {
    labels: processes.map((process) => process.event_name),
    datasets: [
      {
        label: 'Job Duration (seconds)',
        data: processes.map((process) => process.duration_seconds),
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>Process Statistics</Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>
              <TableSortLabel
                active={orderBy === 'event_name'}
                direction={orderBy === 'event_name' ? order : 'asc'}
                onClick={() => handleSort('event_name')}
              >
                Event Name
              </TableSortLabel>
            </TableCell>
            <TableCell>
              <TableSortLabel
                active={orderBy === 'business_date'}
                direction={orderBy === 'business_date' ? order : 'asc'}
                onClick={() => handleSort('business_date')}
              >
                Business Date
              </TableSortLabel>
            </TableCell>
            <TableCell>
              <TableSortLabel
                active={orderBy === 'start_time'}
                direction={orderBy === 'start_time' ? order : 'asc'}
                onClick={() => handleSort('start_time')}
              >
                Start Time
              </TableSortLabel>
            </TableCell>
            <TableCell>
              <TableSortLabel
                active={orderBy === 'end_time'}
                direction={orderBy === 'end_time' ? order : 'asc'}
                onClick={() => handleSort('end_time')}
              >
                End Time
              </TableSortLabel>
            </TableCell>
            <TableCell>
              <TableSortLabel
                active={orderBy === 'duration_seconds'}
                direction={orderBy === 'duration_seconds' ? order : 'asc'}
                onClick={() => handleSort('duration_seconds')}
              >
                Duration (seconds)
              </TableSortLabel>
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {sortedProcesses.map((process) => (
            <TableRow key={process._id}>
              <TableCell>{process.event_name}</TableCell>
              <TableCell>{process.business_date}</TableCell>
              <TableCell>{new Date(process.start_time).toLocaleString()}</TableCell>
              <TableCell>{new Date(process.end_time).toLocaleString()}</TableCell>
              <TableCell>{process.duration_seconds}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <Box mt={4}>
        <Bar
          data={chartData}
          options={{
            scales: {
              y: {
                beginAtZero: true,
              },
            },
          }}
        />
      </Box>
    </Box>
  );
};

export default ProcessStatistics;
