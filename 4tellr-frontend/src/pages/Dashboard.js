// src/pages/Dashboard.js
import React, { useEffect, useState } from 'react';
import SummaryMetrics from "../components/dashboard/SummaryMetrics";
import GroupMetrics from "../components/dashboard/GroupMetrics";
import { Grid, Paper, Typography, Box} from '@mui/material';
const Dashboard = () => {

  useEffect(() => {
  }, []);

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" gutterBottom>
        All Events
      </Typography>
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
    </Box>
  );
};

export default Dashboard;
