// src/pages/Dashboard.js
import React, { useContext } from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import SummaryMetrics from '../components/dashboard/SummaryMetrics';
import MiniChartComponent from '../components/MiniChartComponent';
import MiniGanttChartD3 from '../components/MiniGanttChart';
import { EventsContext } from '../contexts/EventsContext';
import { filterFavouriteEvents } from '../utils/FilterFavouriteEvents';
import '../styles/GantChartD3.css';

const Dashboard = () => {
  const { events, favouriteGroups, metrics, favouriteMetrics, ongoingProcesses, upcomingProcesses, justFinishedProcesses } = useContext(EventsContext);

  const renderGroupCharts = () => {
    if (Array.isArray(favouriteGroups) && favouriteGroups.length > 0) {
      return favouriteGroups.map((group, index) => {
        const groupEvents = filterFavouriteEvents(events, [group]);
        return (
          <Box key={index} mb={2} style={{ flex: '0 0 auto', width: '12cm', height: '7cm' }}>
            <Paper style={{ width: '100%', height: '100%' }}>
              <Typography variant="h6" gutterBottom>{group.group_name}</Typography>
              <MiniChartComponent rawData={groupEvents} width="100%" height="90%" />
            </Paper>
          </Box>
        );
      });
    } else {
      return (
        <Box mb={2} style={{ flex: '0 0 auto', width: '12cm', height: '7cm' }}>
          <Paper style={{ width: '100%', height: '90%' }}>
            <Typography variant="h6" gutterBottom>NO GROUPS</Typography>
          </Paper>
        </Box>
      );
    }
  };

    function renderGanttCharts() {
         return (
            <Box display="flex">
              <Box>
                <Typography variant="h6">Upcoming</Typography>
                <MiniGanttChartD3 data={upcomingProcesses} width={450} height={300} textSize={10} />
              </Box>
              <Box>
                <Typography variant="h6">Ongoing</Typography>
                <MiniGanttChartD3 data={ongoingProcesses} width={450} height={300} textSize={10} />
              </Box>
              <Box>
                <Typography variant="h6">Just Finished</Typography>
                <MiniGanttChartD3 data={justFinishedProcesses} width={450} height={300} textSize={10} />
              </Box>
            </Box>
          );
    }


    return (
    <Box marginTop={3}>
      <Grid container spacing={3} >
        <Grid item xs={12}>
          <SummaryMetrics metrics={metrics} />
        </Grid>
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom>
            Favourite Groups
          </Typography>
          <SummaryMetrics metrics={favouriteMetrics} />
        </Grid>
      </Grid>
      <Grid mt={4} display="flex" overflow="auto" flexDirection="row">
        {renderGroupCharts()}
      </Grid>
      <Grid mt={4} display="flex" overflow="auto" flexDirection="row">
        {renderGanttCharts()}
      </Grid>
    </Box>
  );
};

export default Dashboard;
