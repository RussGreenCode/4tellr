// src/pages/Group.js
import React, { useState, useEffect, useContext } from 'react';
import { Box, Button, Typography, TextField, List, ListItem, ListItemText } from '@mui/material';
import DualListBox from 'react-dual-listbox';
import 'react-dual-listbox/lib/react-dual-listbox.css';
import axios from 'axios';
import { EventsContext } from '../contexts/EventsContext';
import '../styles/GroupManagement.css';
import config from '../config';

const GroupManagement = () => {
  const { setGroupList } = useContext(EventsContext);
  const [availableOptions, setAvailableOptions] = useState([]);
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [groupName, setGroupName] = useState('');
  const [description, setDescription] = useState('');
  const [groups, setGroups] = useState([]);
  const [filteredGroups, setFilteredGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [favoriteGroup, setFavoriteGroup] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');


  useEffect(() => {
    fetchGroupList();
    fetchAvailableOptions();
  }, []);

  const fetchAvailableOptions = async () => {
    try {
      const response = await axios.get(`${config.baseUrl}/api/get_expectation_list`);
      setAvailableOptions(response.data.map(event => ({ value: event.event_name_and_status, label: event.event_name_and_status })));
    } catch (error) {
      console.error('Error fetching available options:', error);
    }
  };

  const fetchGroupList = async (date) => {
    try {
      console.log('Refreshing Group List:');
      const response = await axios.get(`${config.baseUrl}/api/get_groups`);
      setGroups(response.data);
      setGroupList(response.data);
      setFilteredGroups(response.data);
    } catch (error) {
      console.error('Error refreshing group list:', error)
    }

  };



  const handleSaveGroup = async () => {
    try {
      const newGroup = { name: groupName, description, events: selectedOptions };
      await axios.post(`${config.baseUrl}/api/save_group`, newGroup);
      fetchGroupList();
      resetForm();
    } catch (error) {
      console.error('Error saving group:', error);
    }
  };

  const handleUpdateGroup = async () => {
    if (selectedGroup && groupName && selectedOptions.length > 0) {
      try {
        await axios.put(`${config.baseUrl}/api/update_group/${selectedGroup}`, {
          groupName,
          description,
          events: selectedOptions,
        });
        fetchGroupList();
        resetForm();
      } catch (error) {
        console.error('Error updating group:', error);
      }
    } else {
      alert('Group name and events must not be empty.');
    }
  };

  const handleDeleteGroup = async (groupToDelete) => {
    try {
      await axios.post(`${config.baseUrl}/api/delete_group`, { name: groupToDelete.group_name });
      fetchGroupList();
      resetForm();

    } catch (error) {
      console.error('Error deleting group:', error);
    }
  };

  const handleEditGroup = async (group) => {
    try {
      const response = await axios.post(`${config.baseUrl}/api/get_group_details`, { name: group.group_name });
      const retrievedGroup = response.data;


      setGroupName(retrievedGroup.group_name);
      setDescription(retrievedGroup.description);
      setSelectedOptions(retrievedGroup.events);
    } catch (error) {
      console.error('Error fetching group details:', error);
    }
  };

  const handleFavoriteGroup = async (groupId) => {
    setFavoriteGroup(groupId);
    try {
      await axios.post(`${config.baseUrl}/api/favorite_group`, { groupId });
    } catch (error) {
      console.error('Error setting favorite group:', error);
    }
  };

  const resetForm = () => {
    setGroupName('');
    setDescription('');
    setSelectedOptions([]);
    setSelectedGroup(null);
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    filterGroups(e.target.value);
  };

  const filterGroups = (term) => {
    if (term) {
      const filtered = groups.filter(group => group.group_name.toLowerCase().includes(term.toLowerCase()));
      setFilteredGroups(filtered);
    } else {
      setFilteredGroups(groups);
    }
  };

  return (
    <Box p={2}>
      <Typography variant="h4" gutterBottom>
        Manage Event Groups
      </Typography>
      <Box mb={2}>
        <TextField
          label="Group Name"
          value={groupName}
          onChange={(e) => setGroupName(e.target.value)}
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
      <DualListBox
        options={availableOptions}
        selected={selectedOptions}
        onChange={(selected) => setSelectedOptions(selected)}
        icons={{
          moveLeft: '<',
          moveAllLeft: '<<',
          moveRight: '>',
          moveAllRight: '>>',
        }}
        showHeaderLabels
        availableHeader="Available options"
        selectedHeader="Chosen options"
        filterPlaceholder="Filter options"
        preserveSelectOrder
        canFilter
      />
      <Box mt={2}>
        {selectedGroup ? (
          <Button
            variant="contained"
            color="primary"
            onClick={handleUpdateGroup}
            disabled={!groupName || selectedOptions.length === 0}
          >
            Update Group
          </Button>
        ) : (
          <Button
            variant="contained"
            color="primary"
            onClick={handleSaveGroup}
            disabled={!groupName || selectedOptions.length === 0}
          >
            Save Group
          </Button>
        )}
        <Button onClick={resetForm} style={{ marginLeft: '10px' }}>
          Clear
        </Button>
      </Box>
      <Box mt={4}>
        <Typography variant="h5" gutterBottom>
          Existing Groups
        </Typography>
        <Box mb={2}>
          <TextField
            label="Search Groups"
            value={searchTerm}
            onChange={handleSearchChange}
            variant="outlined"
            fullWidth
          />
        </Box>
        <List className="scrollable-list">
          {filteredGroups.map((group, index) => (
            <ListItem key={index} button onClick={() => handleEditGroup(group)}>
              <ListItemText primary={group.group_name} secondary={group.description} />
              <Button variant="contained" color="secondary" onClick={() => handleDeleteGroup(group)}>
                Delete
              </Button>
              <Button
                variant="contained"
                color={favoriteGroup === group.groupId ? 'default' : 'primary'}
                onClick={() => handleFavoriteGroup(group.groupId)}
                style={{ marginLeft: '10px' }}
              >
                {favoriteGroup === group.groupId ? 'Unfavorite' : 'Favorite'}
              </Button>
            </ListItem>
          ))}
        </List>
      </Box>
    </Box>
  );
};

export default GroupManagement;
