// src/pages/Dashboard.js
import React, { useContext } from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import SummaryMetrics from '../components/dashboard/SummaryMetrics';
import MiniChartComponent from '../components/MiniChartComponent';
import { EventsContext } from '../contexts/EventsContext';
import { filterFavouriteEvents } from '../utils/FilterFavouriteEvents';

const Dashboard = () => {
  const { events, favouriteGroups, metrics, favouriteMetrics } = useContext(EventsContext);

  const renderGroupCharts = () => {
    if (Array.isArray(favouriteGroups) && favouriteGroups.length > 0) {
      return favouriteGroups.map((group, index) => {
        const groupEvents = filterFavouriteEvents(events, [group]);
        return (
          <Box key={index} mb={2} style={{ flex: '0 0 auto', width: '12cm', height: '6cm' }}>
            <Paper style={{ width: '100%', height: '100%' }}>
              <Typography variant="h6" gutterBottom>{group.group_name}</Typography>
              <MiniChartComponent rawData={groupEvents} width="100%" height="100%" />
            </Paper>
          </Box>
        );
      });
    } else {
      return (
        <Box mb={2} style={{ flex: '0 0 auto', width: '12cm', height: '6cm' }}>
          <Paper style={{ width: '100%', height: '100%' }}>
            <Typography variant="h6" gutterBottom>NO GROUPS</Typography>
          </Paper>
        </Box>
      );
    }
  };

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
    </Box>
  );
};

export default Dashboard;
