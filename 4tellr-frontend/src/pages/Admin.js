import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Grid } from '@mui/material';
import '../styles/App.css';

const Admin = () => {
  const [businessDate, setBusinessDate] = useState('');
  const [noOfDays, setNoOfDays] = useState('');

  const baseUrl = process.env.REACT_APP_BASE_URL;

  const handleGenerateExpectations = () => {
    if (!businessDate) {
      alert('Please enter a valid business date.');
      return;
    }

    fetch(`${baseUrl}/api/events/generate-expectations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ businessDate }),
    })
      .then(response => response.json())
      .then(data => {
        alert('Expectations generated successfully.');
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Failed to generate expectations.');
      });
  };

  const handleDeleteEventsForBusinessDates = () => {
    if (!businessDate || !noOfDays) {
      alert('Please enter a valid starting date and number of days.');
      return;
    }

    const startDate = new Date(businessDate);
    const numberOfDays = parseInt(noOfDays, 10);
    if (isNaN(numberOfDays) || numberOfDays <= 0) {
      alert('Please enter a valid number of days.');
      return;
    }

    const businessDates = [];
    for (let i = 0; i < numberOfDays; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      businessDates.push(date.toISOString().split('T')[0]);
    }

    fetch(`${baseUrl}/api/events/delete_events`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ businessDates }),
    })
      .then(response => response.json())
      .then(data => {
        alert('Events deleted successfully.');
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Failed to delete events.');
      });
  };

  const handleUpdateExpectedTimes = () => {
    fetch(`${baseUrl}/api/events/expected-times/update`, {
      method: 'POST',
    })
      .then(response => response.json())
      .then(data => {
        alert('Expected times updated successfully.');
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Failed to update expected times.');
      });
  };

  return (
    <Box className="admin-container">
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>

      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} sm={6} md={4}>
          <TextField
            label="Business Date"
            type="date"
            value={businessDate}
            onChange={(e) => setBusinessDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            fullWidth
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={handleGenerateExpectations}
          >
            Generate Expectations
          </Button>
        </Grid>
      </Grid>

      <Grid container spacing={2} alignItems="center" style={{ marginTop: '16px' }}>
        <Grid item xs={12} sm={6} md={4}>
          <TextField
            label="Starting Date"
            type="date"
            value={businessDate}
            onChange={(e) => setBusinessDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            fullWidth
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <TextField
            label="Number of Days"
            type="number"
            value={noOfDays}
            onChange={(e) => setNoOfDays(e.target.value)}
            InputLabelProps={{ shrink: true }}
            fullWidth
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={handleDeleteEventsForBusinessDates}
          >
            Delete Events
          </Button>
        </Grid>
      </Grid>

      <Grid container spacing={2} alignItems="center" style={{ marginTop: '16px' }}>
        <Grid item xs={12} sm={6} md={4}>
          <Button
            variant="contained"
            color="secondary"
            fullWidth
            onClick={handleUpdateExpectedTimes}
          >
            Update Expected Times
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Admin;
