// src/pages/FavouriteAlerts.js
import React, { useState, useEffect, useContext } from 'react';
import { Box, Button, Typography, List, ListItem, ListItemText, ListItemIcon, Checkbox, TextField } from '@mui/material';
import axios from 'axios';
import { EventsContext } from '../contexts/EventsContext';
import '../styles/GroupManagement.css';

const FavouriteAlerts = () => {
  const {currentUser, fetchUser} = useContext(EventsContext);
  const [availableAlerts, setAvailableAlerts] = useState([]);
  const [favouriteAlerts, setFavouriteAlerts] = useState([]);
  const [selectedAvailable, setSelectedAvailable] = useState([]);
  const [selectedFavourite, setSelectedFavourite] = useState([]);
  const [availableFilter, setAvailableFilter] = useState('');
  const [favouriteFilter, setFavouriteFilter] = useState('');

  useEffect(() => {
    fetchAlerts();
  }, []);

  useEffect(() => {
    if (currentUser && currentUser.favourite_alerts) {
      setFavouriteAlerts(currentUser.favourite_alerts);
    }
  }, [currentUser]);

  const fetchAlerts = async () => {
    try {

      const response = await axios.get('http://127.0.0.1:5000/api/alerts');
      const alertList = response.data;

      const allAlerts = alertList.map(alert => alert.alert_name);
      const filteredAlerts = allAlerts.filter(alert => !currentUser.favourite_alerts.includes(alert));
      setAvailableAlerts(filteredAlerts);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  const handleTransferToFavourite = () => {
    const newFavourites = [...favouriteAlerts, ...selectedAvailable];
    setFavouriteAlerts(newFavourites);
    setAvailableAlerts(availableAlerts.filter(alert => !selectedAvailable.includes(alert)));
    setSelectedAvailable([]);
  };

  const handleTransferToAvailable = () => {
    const newAvailable = [...availableAlerts, ...selectedFavourite];
    setAvailableAlerts(newAvailable);
    setFavouriteAlerts(favouriteAlerts.filter(alert => !selectedFavourite.includes(alert)));
    setSelectedFavourite([]);
  };

  const handleTransferAllToFavourite = () => {
    const newFavourites = [...favouriteAlerts, ...availableAlerts];
    setFavouriteAlerts(newFavourites);
    setAvailableAlerts([]);
    setSelectedAvailable([]);
  };

  const handleTransferAllToAvailable = () => {
    const newAvailable = [...availableAlerts, ...favouriteAlerts];
    setAvailableAlerts(newAvailable);
    setFavouriteAlerts([]);
    setSelectedFavourite([]);
  };

  const handleSaveFavourites = async () => {
    try {
      await axios.post('http://127.0.0.1:5000/api/save_user_favourite_alerts', {
        email: currentUser.email,
        favourite_alerts: favouriteAlerts
      });

      fetchUser(currentUser.email);

    } catch (error) {
      console.error('Error saving favourite alerts:', error);
    }
  };

  const filteredAvailableAlerts = availableAlerts.filter(alert =>
    alert.toLowerCase().includes(availableFilter.toLowerCase())
  );

  const filteredFavouriteAlerts = favouriteAlerts.filter(alert =>
    alert.toLowerCase().includes(favouriteFilter.toLowerCase())
  );

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Manage Favourite Alerts
      </Typography>
      <Box display="flex" justifyContent="space-between" mt={2}>
        <Box flex={1} mr={1}>
          <Typography variant="h6">Available Alerts</Typography>
          <TextField
            label="Search..."
            variant="outlined"
            fullWidth
            margin="normal"
            value={availableFilter}
            onChange={(e) => setAvailableFilter(e.target.value)}
          />
          <Box height="300px" overflow="auto" border="1px solid lightgrey">
            <List>
              {filteredAvailableAlerts.map((alert, index) => (
                <ListItem key={index} button onClick={() => setSelectedAvailable(prev => prev.includes(alert) ? prev.filter(item => item !== alert) : [...prev, alert])}>
                  <ListItemText primary={alert} />
                  <ListItemIcon>
                    <Checkbox edge="end" checked={selectedAvailable.includes(alert)} tabIndex={-1} disableRipple />
                  </ListItemIcon>
                </ListItem>
              ))}
            </List>
          </Box>
        </Box>
        <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" mx={2}>
          <Button onClick={handleTransferToFavourite} disabled={selectedAvailable.length === 0} style={{ backgroundColor: '#f0f0f0', marginBottom: '5px' }}>
            &gt;
          </Button>
          <Button onClick={handleTransferAllToFavourite} style={{ backgroundColor: '#f0f0f0', marginBottom: '5px' }}>
            &gt;&gt;
          </Button>
          <Button onClick={handleTransferAllToAvailable} style={{ backgroundColor: '#f0f0f0', marginBottom: '5px' }}>
            &lt;&lt;
          </Button>
          <Button onClick={handleTransferToAvailable} disabled={selectedFavourite.length === 0} style={{ backgroundColor: '#f0f0f0', marginBottom: '5px' }}>
            &lt;
          </Button>
        </Box>
        <Box flex={1} ml={1}>
          <Typography variant="h6">Favourite Alerts</Typography>
          <TextField
            label="Search..."
            variant="outlined"
            fullWidth
            margin="normal"
            value={favouriteFilter}
            onChange={(e) => setFavouriteFilter(e.target.value)}
          />
          <Box height="300px" overflow="auto" border="1px solid lightgrey">
            <List>
              {filteredFavouriteAlerts.map((alert, index) => (
                <ListItem key={index} button onClick={() => setSelectedFavourite(prev => prev.includes(alert) ? prev.filter(item => item !== alert) : [...prev, alert])}>
                  <ListItemText primary={alert} />
                  <ListItemIcon>
                    <Checkbox edge="end" checked={selectedFavourite.includes(alert)} tabIndex={-1} disableRipple />
                  </ListItemIcon>
                </ListItem>
              ))}
            </List>
          </Box>
        </Box>
      </Box>
      <Box mt={2}>
        <Button variant="contained" color="primary" onClick={handleSaveFavourites}>
          Save Favourites
        </Button>
      </Box>
    </Box>
  );
};

export default FavouriteAlerts;
