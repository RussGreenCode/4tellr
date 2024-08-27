// src/pages/EventDependencies.js
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Checkbox,
  TextField,
  Autocomplete
} from '@mui/material';
import axios from 'axios';
import '../styles/GroupManagement.css';
import config from '../config';

const EventDependencies = () => {
  // New Metadata Constants
  const [eventMetadataList, setEventMetadataList] = useState([]);
  const [startedEventMetadataList, setStartedEventMetadataList] = useState([]);
  const [successEventMetadataList, setSuccessEventMetadataList] = useState([]);
  const [selectedMetadataId, setSelectedMetadataId] = useState('');
  const [selectedMetadata, setSelectedMetadata] = useState(null);

  // OLD event CONstants
  const [availableEvents, setAvailableEvents] = useState([]);
  const [dependentEvents, setDependentEvents] = useState([]);
  const [selectedAvailable, setSelectedAvailable] = useState([]);
  const [selectedDependent, setSelectedDependent] = useState([]);
  const [availableFilter, setAvailableFilter] = useState('');
  const [favouriteFilter, setFavouriteFilter] = useState('');

  useEffect(() => {
    fetchEventMetadataList();
  }, []);

  useEffect(() => {

    fetchEventMetadata()

  }, [selectedMetadataId, eventMetadataList, successEventMetadataList]);

  const fetchEventMetadata = async () => {

    if (selectedMetadataId) {
      try {
        const response = await axios.get(`${config.baseUrl}/api/event/get_event_metadata`, {params: {id: selectedMetadataId}});
        if (response.data) {
          const selected =  response.data
          setSelectedMetadata(selected);
          setAvailableEvents(successEventMetadataList.filter(event => event.event_name !== selected.event_name).map(event => event.event_name));
          setDependentEvents(selected.dependencies || []);

        } else {
          console.error('No metadata found for the selected ID ', selectedMetadataId);
        }
      } catch (error) {
        console.error('Error fetching metadata:', error);
      }
    }
  }

  const fetchEventMetadataList = async () => {
    try {
      const response = await axios.get(`${config.baseUrl}/api/event/event_metadata_list`);
      if (response.data && response.data.length > 0) {
        setEventMetadataList(response.data);
        const startedEvents = response.data.filter(event => event.event_status === 'STARTED');
        setStartedEventMetadataList(startedEvents);
        const successEvents = response.data.filter(event => event.event_status === 'SUCCESS');
        setSuccessEventMetadataList(successEvents);
      } else {
        console.error('No event metadata found');
      }
    } catch (error) {
      console.error('Error fetching event metadata list:', error);
    }
  };

  const handleTransferToFavourite = () => {
    const newDependents = [...dependentEvents, ...selectedAvailable];
    setDependentEvents(newDependents);
    setAvailableEvents(availableEvents.filter(event => !selectedAvailable.includes(event)));
    setSelectedAvailable([]);
  };

  const handleTransferToAvailable = () => {
    const newAvailable = [...availableEvents, ...selectedDependent];
    setAvailableEvents(newAvailable);
    setDependentEvents(dependentEvents.filter(event => !selectedDependent.includes(event)));
    setSelectedDependent([]);
  };

  const handleTransferAllToFavourite = () => {
    const newDependent = [...dependentEvents, ...availableEvents];
    setDependentEvents(newDependent);
    setAvailableEvents([]);
    setSelectedAvailable([]);
  };

  const handleTransferAllToAvailable = () => {
    const newAvailable = [...availableEvents, ...dependentEvents];
    setAvailableEvents(newAvailable);
    setDependentEvents([]);
    setSelectedDependent([]);
  };

  const handleSaveFavourites = async () => {
    try {
      const updatedMetadata = {
        ...selectedMetadata,
        dependencies: dependentEvents
      };
      await axios.put(`${config.baseUrl}/api/event/event_metadata_dependencies`, updatedMetadata);
      console.log('Favourites saved successfully');
    } catch (error) {
      console.error('Error saving favourite events:', error);
    }
  };

  const filteredAvailableevents = availableEvents.filter(event =>
    event.toLowerCase().includes(availableFilter.toLowerCase())
  );

  const filteredFavouriteevents = dependentEvents.filter(event =>
    event.toLowerCase().includes(favouriteFilter.toLowerCase())
  );

  const handleMetadataSelect = (event, value) => {
    setSelectedMetadataId(value ? value._id : '');
  };

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>Manage Event Dependencies</Typography>
      <Box mb={3}>
        <Autocomplete
          options={startedEventMetadataList}
          getOptionLabel={(option) => `${option.event_name} - ${option.event_status}`}
          onChange={handleMetadataSelect}
          renderInput={(params) => <TextField {...params} label="Search Event Metadata" variant="outlined" />}
        />
      </Box>
      <Box display="flex" justifyContent="space-between" mt={2}>
        <Box flex={1} mr={1}>
          <Typography variant="h6">Available Events</Typography>
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
              {filteredAvailableevents.map((event, index) => (
                <ListItem key={index} button onClick={() => setSelectedAvailable(prev => prev.includes(event) ? prev.filter(item => item !== event) : [...prev, event])}>
                  <ListItemText primary={event} />
                  <ListItemIcon>
                    <Checkbox edge="end" checked={selectedAvailable.includes(event)} tabIndex={-1} disableRipple />
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
          <Button onClick={handleTransferToAvailable} disabled={selectedDependent.length === 0} style={{ backgroundColor: '#f0f0f0', marginBottom: '5px' }}>
            &lt;
          </Button>
        </Box>
        <Box flex={1} ml={1}>
          <Typography variant="h6">Event Dependencies</Typography>
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
              {filteredFavouriteevents.map((event, index) => (
                <ListItem key={index} button onClick={() => setSelectedDependent(prev => prev.includes(event) ? prev.filter(item => item !== event) : [...prev, event])}>
                  <ListItemText primary={event} />
                  <ListItemIcon>
                    <Checkbox edge="end" checked={selectedDependent.includes(event)} tabIndex={-1} disableRipple />
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

export default EventDependencies;
