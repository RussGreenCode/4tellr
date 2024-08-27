// src/pages/FavouriteGroups.js
import React, { useState, useEffect, useContext } from 'react';
import { Box, Button, Typography, List, ListItem, ListItemText, ListItemIcon, Checkbox, TextField } from '@mui/material';
import axios from 'axios';
import { EventsContext } from '../contexts/EventsContext';
import '../styles/GroupManagement.css';
import config from '../config';

const FavouriteGroups = () => {
  const { currentUser, fetchUser, groupList, setGroupList, fetchGroupList} = useContext(EventsContext);
  const [availableGroups, setAvailableGroups] = useState([]);
  const [favouriteGroups, setFavouriteGroups] = useState([]);
  const [selectedAvailable, setSelectedAvailable] = useState([]);
  const [selectedFavourite, setSelectedFavourite] = useState([]);
  const [availableFilter, setAvailableFilter] = useState('');
  const [favouriteFilter, setFavouriteFilter] = useState('');

  useEffect(() => {
    fetchGroups();
  }, []);

  useEffect(() => {
    if (currentUser && currentUser.favourite_groups) {
      setFavouriteGroups(currentUser.favourite_groups);
    }
  }, [currentUser]);

  const fetchGroups = async () => {
    try {
      //const response = await axios.get(`${config.baseUrl}/api/get_groups`);
      fetchGroupList()
      const allGroups = groupList.map(group => group.group_name);
      const filteredGroups = allGroups.filter(group => !currentUser.favourite_groups.includes(group));
      setAvailableGroups(filteredGroups);
    } catch (error) {
      console.error('Error fetching groups:', error);
    }
  };

  const handleTransferToFavourite = () => {
    const newFavourites = [...favouriteGroups, ...selectedAvailable];
    setFavouriteGroups(newFavourites);
    setAvailableGroups(availableGroups.filter(group => !selectedAvailable.includes(group)));
    setSelectedAvailable([]);
  };

  const handleTransferToAvailable = () => {
    const newAvailable = [...availableGroups, ...selectedFavourite];
    setAvailableGroups(newAvailable);
    setFavouriteGroups(favouriteGroups.filter(group => !selectedFavourite.includes(group)));
    setSelectedFavourite([]);
  };

  const handleTransferAllToFavourite = () => {
    const newFavourites = [...favouriteGroups, ...availableGroups];
    setFavouriteGroups(newFavourites);
    setAvailableGroups([]);
    setSelectedAvailable([]);
  };

  const handleTransferAllToAvailable = () => {
    const newAvailable = [...availableGroups, ...favouriteGroups];
    setAvailableGroups(newAvailable);
    setFavouriteGroups([]);
    setSelectedFavourite([]);
  };

  const handleSaveFavourites = async () => {
    try {
      await axios.post(`${config.baseUrl}/api/save_user_favourite_groups`, {
        email: currentUser.email,
        favourite_groups: favouriteGroups
      });

      fetchUser(currentUser.email)

    } catch (error) {
      console.error('Error saving favourite groups:', error);
    }

  };

  const filteredAvailableGroups = availableGroups.filter(group =>
    group.toLowerCase().includes(availableFilter.toLowerCase())
  );

  const filteredFavouriteGroups = favouriteGroups.filter(group =>
    group.toLowerCase().includes(favouriteFilter.toLowerCase())
  );

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Manage Favourite Groups
      </Typography>
      <Box display="flex" justifyContent="space-between" mt={2}>
        <Box flex={1} mr={1}>
          <Typography variant="h6">Available Groups</Typography>
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
              {filteredAvailableGroups.map((group, index) => (
                <ListItem key={index} button onClick={() => setSelectedAvailable(prev => prev.includes(group) ? prev.filter(item => item !== group) : [...prev, group])}>
                  <ListItemText primary={group} />
                  <ListItemIcon>
                    <Checkbox edge="end" checked={selectedAvailable.includes(group)} tabIndex={-1} disableRipple />
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
          <Typography variant="h6">Favourite Groups</Typography>
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
              {filteredFavouriteGroups.map((group, index) => (
                <ListItem key={index} button onClick={() => setSelectedFavourite(prev => prev.includes(group) ? prev.filter(item => item !== group) : [...prev, group])}>
                  <ListItemText primary={group} />
                  <ListItemIcon>
                    <Checkbox edge="end" checked={selectedFavourite.includes(group)} tabIndex={-1} disableRipple />
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

export default FavouriteGroups;
