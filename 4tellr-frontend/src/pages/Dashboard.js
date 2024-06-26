// src/pages/Dashboard.js
import React, { useContext } from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import SummaryMetrics from '../components/dashboard/SummaryMetrics';
import GroupMetrics from '../components/dashboard/GroupMetrics';
import MiniChartComponent from '../components/MiniChartComponent';
import { EventsContext } from '../contexts/EventsContext';
import { filterFavouriteEvents } from '../utils/filterFavouriteEvents';

const Dashboard = () => {
  const { events, favouriteGroups } = useContext(EventsContext);

  const renderGroupCharts = () => {
    if (Array.isArray(favouriteGroups) && favouriteGroups.length > 0) {
      return favouriteGroups.map((group, index) => {
        const groupEvents = filterFavouriteEvents(events, [group]);
        return (
          <Box key={index} mb={2} style={{ flex: '0 0 auto', width: '6cm', height: '3cm' }}>
            <Paper style={{ width: '100%', height: '100%' }}>
              <Typography variant="h6" gutterBottom>{group.group_name}</Typography>
              <MiniChartComponent rawData={groupEvents} width="100%" height="100%" />
            </Paper>
          </Box>
        );
      });
    } else {
      return (
        <Box mb={2} style={{ flex: '0 0 auto', width: '6cm', height: '3cm' }}>
          <Paper style={{ width: '100%', height: '100%' }}>
            <Typography variant="h6" gutterBottom>NO GROUPS</Typography>
          </Paper>
        </Box>
      );
    }
  };

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <SummaryMetrics />
        </Grid>
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom>
            Favourite Groups
          </Typography>
          <GroupMetrics />
        </Grid>
      </Grid>
      <Grid mt={4} display="flex" overflow="auto" flexDirection="row">
        {renderGroupCharts()}
      </Grid>
    </Box>
  );
};

export default Dashboard;
