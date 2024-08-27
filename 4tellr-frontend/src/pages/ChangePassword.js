// src/pages/UserProfile.js
import React, { useState, useEffect, useContext } from 'react';
import { Box, Button, Typography, TextField, List, ListItem, ListItemText, Checkbox, FormControlLabel, Grid, Paper } from '@mui/material';
import axios from 'axios';
import { EventsContext } from '../contexts/EventsContext';
import '../styles/UserProfile.css';
import config from '../config';


const UserProfile = ({ email }) => {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');


  useEffect(() => {

  }, []);

  const handlePasswordChange = async () => {
    if (newPassword !== confirmPassword) {
      setMessage('New passwords do not match.');
      return;
    }

    try {
      const response = await axios.post(`${config.baseUrl}/api/change_password`, {
        email,
        currentPassword,
        newPassword,
      });
      setMessage(response.data.message);
    } catch (error) {
      setMessage('Error changing password.');
      console.error('Error changing password:', error);
    }

    setCurrentPassword('');
    setConfirmPassword('');
    setNewPassword('');
  };


  return (
    <Box p={2}>
      <Typography variant="h4" gutterBottom>
        User Profile
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper className="profile-paper" elevation={1}>
            <Typography variant="h5" gutterBottom>
              Manage Password
            </Typography>
            <TextField
              label="Current Password"
              type="password"
              variant="outlined"
              fullWidth
              margin="normal"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
            />
            <TextField
              label="New Password"
              type="password"
              variant="outlined"
              fullWidth
              margin="normal"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
            <TextField
              label="Confirm New Password"
              type="password"
              variant="outlined"
              fullWidth
              margin="normal"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
            <Button
              variant="contained"
              color="primary"
              fullWidth
              onClick={handlePasswordChange}
              style={{ marginTop: '1rem' }}
            >
              Change Password
            </Button>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
        </Grid>
      </Grid>
      {message && (
        <Typography variant="body1" color="textSecondary" align="center" style={{ marginTop: '1rem' }}>
          {message}
        </Typography>
      )}
    </Box>
  );
};

export default UserProfile;
