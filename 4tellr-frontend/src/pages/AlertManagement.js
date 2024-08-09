// src/pages/AlertManagement.js
import React, { useState, useEffect, useContext } from 'react';
import {
  Box,
  Button,
  Typography,
  TextField,
  List,
  ListItem,
  ListItemText,
  Autocomplete,
  IconButton
} from '@mui/material';
import axios from 'axios';
import { EventsContext } from '../contexts/EventsContext';
import '../styles/GroupManagement.css';
import { Delete, Edit, FlashOn, Pause, PlayArrow as Resume } from "@mui/icons-material";

const AlertManagement = () => {
  const [alertOptions, setAlertOptions] = useState([]);
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [alertName, setAlertName] = useState('');
  const [description, setDescription] = useState('');
  const [alerts, setAlerts] = useState([]);
  const [filteredAlerts, setFilteredAlerts] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchGroups();
    fetchAlerts();
  }, []);

  const fetchGroups = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/get_groups');
      setGroups(response.data.map(group => ({ value: group.group_name, label: group.group_name })));
    } catch (error) {
      console.error('Error fetching available options:', error);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/alerts');
      setAlertOptions(response.data.map(alert => ({ value: alert.group_name, label: alert.group_name })));
      const alertList = response.data;

      setAlerts(alertList);
      setFilteredAlerts(alertList);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  const handleSaveAlert = async () => {
    const group_name = selectedGroup.value;

    try {
      const newAlert = { alert_name: alertName, description: description, group_name: group_name };
      await axios.post('http://127.0.0.1:5000/api/alerts', newAlert);
      fetchAlerts();
      resetForm();
    } catch (error) {
      console.error('Error saving alert:', error);
    }
  };

  const handleUpdateAlert = async () => {
    if (selectedAlert && alertName && selectedGroup) {
      try {
        await axios.put(`http://127.0.0.1:5000/api/alerts`, {
          alert_name: alertName,
          description,
          group_name: selectedGroup.value,
        });
        fetchAlerts();
        resetForm();
      } catch (error) {
        console.error('Error updating alert:', error);
      }
    } else {
      alert('Alert name and group must not be empty.');
    }
  };

  const handleDeleteAlert = async (alertToDelete) => {
    try {
      await axios.delete(`http://127.0.0.1:5000/api/alerts`, {
        params: { alert_name: alertToDelete.alert_name }
      });
      fetchAlerts();
      resetForm();
    } catch (error) {
      console.error('Error deleting alert:', error);
    }
  };


  const handleEditAlert = async (alert) => {
    try {
      setAlertName(alert.alert_name);
      setDescription(alert.description);
      setSelectedGroup(groups.find(group => group.value === alert.group_name));
      setSelectedAlert(alert.alert_name);
    } catch (error) {
      console.error('Error fetching alert details:', error);
    }
  };

  const resetForm = () => {
    setAlertName('');
    setDescription('');
    setSelectedGroup(null);
    setSelectedAlert(null);
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    filterAlerts(e.target.value);
  };

  const filterAlerts = (term) => {
    if (term) {
      const filtered = alerts.filter(alert => alert.alert_name.toLowerCase().includes(term.toLowerCase()));
      setFilteredAlerts(filtered);
    } else {
      setFilteredAlerts(alerts);
    }
  };

  return (
    <Box p={2}>
      <Typography variant="h4" gutterBottom>
        Alert Management
      </Typography>
      <Box mb={2}>
        <TextField
          label="Alert Name"
          value={alertName}
          onChange={(e) => setAlertName(e.target.value)}
          variant="outlined"
          fullWidth
        />
      </Box>
      <Box mb={2}>
        <TextField
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          variant="outlined"
          fullWidth
        />
      </Box>
      <Autocomplete
        options={groups}
        getOptionLabel={(option) => option.label}
        value={selectedGroup}
        onChange={(event, newValue) => {
          setSelectedGroup(newValue);
        }}
        renderInput={(params) => <TextField {...params} label="Select Group" variant="outlined" />}
      />
      <Box mt={2}>
        {selectedAlert ? (
          <Button
            variant="contained"
            color="primary"
            onClick={handleUpdateAlert}
            disabled={!alertName || !selectedGroup}
          >
            Update Alert
          </Button>
        ) : (
          <Button
            variant="contained"
            color="primary"
            onClick={handleSaveAlert}
            disabled={!alertName || !selectedGroup}
          >
            Save Alert
          </Button>
        )}
        <Button onClick={resetForm} style={{ marginLeft: '10px' }}>
          Clear
        </Button>
      </Box>
      <Box mt={4}>
        <Typography variant="h5" gutterBottom>
          Existing Alerts
        </Typography>
        <Box mb={2}>
          <TextField
            label="Search Alerts"
            value={searchTerm}
            onChange={handleSearchChange}
            variant="outlined"
            fullWidth
          />
        </Box>
        <List className="scrollable-list">
          {filteredAlerts.map((alert, index) => (
            <ListItem key={index} button onClick={() => handleEditAlert(alert)}>
              <ListItemText primary={alert.alert_name} secondary={alert.description} />
              <IconButton edge="end" aria-label="edit" onClick={() => handleEditAlert(alert)}>
                <Edit />
              </IconButton>
              <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteAlert(alert)}>
                <Delete />
              </IconButton>
            </ListItem>
          ))}
        </List>
      </Box>
    </Box>
  );
};

export default AlertManagement;
