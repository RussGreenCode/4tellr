// src/pages/UserProfile.js
import React, { useState, useEffect, useContext } from 'react';
import { Box, Button, Typography, TextField, List, ListItem, ListItemText, Checkbox, FormControlLabel, Grid, Paper } from '@mui/material';
import axios from 'axios';
import { EventsContext } from '../contexts/EventsContext';
import '../styles/UserProfile.css';

const UserProfile = ({ email }) => {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [groups, setGroups] = useState([]);
  const [favoriteGroups, setFavoriteGroups] = useState([]);
  const [message, setMessage] = useState('');

  const { events } = useContext(EventsContext);

  useEffect(() => {
    // Fetch existing groups and favorite groups
    const fetchGroups = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/groups');
        setGroups(response.data.groups);
        const favoriteResponse = await axios.get(`http://127.0.0.1:5000/api/user_favorite_groups?email=${email}`);
        setFavoriteGroups(favoriteResponse.data.favoriteGroups);
      } catch (error) {
        console.error('Error fetching groups:', error);
      }
    };
    fetchGroups();
  }, [email]);

  const handlePasswordChange = async () => {
    if (newPassword !== confirmPassword) {
      setMessage('New passwords do not match.');
      return;
    }

    try {
      const response = await axios.post('http://127.0.0.1:5000/api/change_password', {
        email,
        currentPassword,
        newPassword,
      });
      setMessage(response.data.message);
    } catch (error) {
      setMessage('Error changing password.');
      console.error('Error changing password:', error);
    }
  };

  const handleFavoriteGroupChange = (groupId) => {
    setFavoriteGroups((prevFavorites) =>
      prevFavorites.includes(groupId)
        ? prevFavorites.filter((id) => id !== groupId)
        : [...prevFavorites, groupId]
    );
  };

  const saveFavoriteGroups = async () => {
    try {
      await axios.post('http://127.0.0.1:5000/api/user_favorite_groups', {
        email,
        favoriteGroups,
      });
      setMessage('Favorite groups updated successfully.');
    } catch (error) {
      setMessage('Error updating favorite groups.');
      console.error('Error updating favorite groups:', error);
    }
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
