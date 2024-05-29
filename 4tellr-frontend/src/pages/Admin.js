import React, { useState } from 'react';
import { Box, TextField, Button, Typography } from '@mui/material';
import '../styles/App.css';



const Admin = () => {
  const [businessDate, setBusinessDate] = useState('');

  const baseUrl = process.env.REACT_APP_BASE_URL;

  const handleGenerateExpectations = () => {
    if (!businessDate) {
      alert('Please enter a valid business date.');
      return;
    }

    console.log('baseUrl:', baseUrl);

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
        console.log(data);
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Failed to generate expectations.');
      });
  };

  const handleDeleteEventsForBusinessDate = () => {
    if (!businessDate) {
      alert('Please enter a valid business date.');
      return;
    }

    console.log('baseUrl:', baseUrl);

    fetch(`${baseUrl}/api/events/delete_events`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ businessDate }),
    })
      .then(response => response.json())
      .then(data => {
        alert('Events Deleted successfully.');
        console.log(data);
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Failed to generate expectations.');
      });
  };

  const handleUpdateExpectedTimes = () => {
    fetch(`${baseUrl}/api/events/expected-times/update`, {
      method: 'POST',
    })
      .then(response => response.json())
      .then(data => {
        alert('Expected times updated successfully.');
        console.log(data);
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

      <Box className="function-row">
        <TextField
          label="Business Date"
          type="date"
          value={businessDate}
          onChange={(e) => setBusinessDate(e.target.value)}
          InputLabelProps={{ shrink: true }}
        />
        <Button variant="contained" color="primary" onClick={handleGenerateExpectations}>
          Generate Expectations
        </Button>
      </Box>

      <Box className="function-row">
        <TextField
          label="Business Date"
          type="date"
          value={businessDate}
          onChange={(e) => setBusinessDate(e.target.value)}
          InputLabelProps={{ shrink: true }}
        />
        <Button variant="contained" color="primary" onClick={handleDeleteEventsForBusinessDate}>
          Delete Events
        </Button>
      </Box>

      <Box className="function-row">
        <Button variant="contained" color="secondary" onClick={handleUpdateExpectedTimes}>
          Update Expected Times
        </Button>
      </Box>
    </Box>
  );
};

export default Admin;
