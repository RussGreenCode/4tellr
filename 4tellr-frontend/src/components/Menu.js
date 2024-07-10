// src/components/Menu.js
import React, { useContext, useState } from 'react';
import { List, ListItem, ListItemText, Box, ListSubheader, Collapse, ListItemIcon } from '@mui/material';
import { ExpandLess, ExpandMore } from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import { EventsContext } from '../contexts/EventsContext';
import '../styles/App.css';
import { exportToCSV } from '../utils/ExportUtils';
import axios from 'axios';

const Menu = ({ setIsAuthenticated }) => {
  const { events, filteredEvents } = useContext(EventsContext);
  const [profileOpen, setProfileOpen] = useState(false);
  const [analyticsOpen, setAnalyticsOpen] = useState(false);
  const [adminOpen, setAdminOpen] = useState(false);
  const [exportOpen, setExportOpen] = useState(false);
  const navigate = useNavigate();

  const handleExportFull = () => {
    exportToCSV(events, 'full_dataset.csv');
  };

  const handleExportFiltered = () => {
    exportToCSV(filteredEvents, 'filtered_dataset.csv');
  };

  const handleLogout = async () => {
    try {
      await axios.post('http://127.0.0.1:5000/api/logout');
      setIsAuthenticated(false);
      navigate('/');
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  const handleProfileClick = () => {
    setProfileOpen(!profileOpen);
  };

  const handleAnalyticsClickClick = () => {
    setAnalyticsOpen(!analyticsOpen);
  };

  const handleAdminClick = () => {
    setAdminOpen(!adminOpen);
  };

  const handleExportClick = () => {
    setExportOpen(!exportOpen);
  };

  return (
    <Box>
      <List>
        <ListItem button component={Link} to="/">
          <ListItemText primary="Dashboard" />
        </ListItem>
        <ListItem button component={Link} to="/details">
          <ListItemText primary="Details" />
        </ListItem>
         <ListItem button onClick={handleAnalyticsClickClick}>
          <ListItemText primary="Analytics" />
          {analyticsOpen ? <ExpandLess /> : <ExpandMore />}
        </ListItem>
        <Collapse in={analyticsOpen} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            <ListItem button component={Link} to="/changePassword" sx={{ pl: 4 }}>
              <ListItemText primary="Change Password" primaryTypographyProps={{ fontSize: '0.9rem', color: 'text.secondary' }} />
            </ListItem>
          </List>
        </Collapse>
        <ListItem button onClick={handleProfileClick}>
          <ListItemText primary="My Profile" />
          {profileOpen ? <ExpandLess /> : <ExpandMore />}
        </ListItem>
        <Collapse in={profileOpen} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            <ListItem button component={Link} to="/changePassword" sx={{ pl: 4 }}>
              <ListItemText primary="Change Password" primaryTypographyProps={{ fontSize: '0.9rem', color: 'text.secondary' }} />
            </ListItem>
            <ListItem button component={Link} to="/favouriteGroups" sx={{ pl: 4 }}>
              <ListItemText primary="Manage Groups" primaryTypographyProps={{ fontSize: '0.9rem', color: 'text.secondary' }} />
            </ListItem>
          </List>
        </Collapse>
        <ListItem button onClick={handleAdminClick}>
          <ListItemText primary="Admin" />
          {adminOpen ? <ExpandLess /> : <ExpandMore />}
        </ListItem>
        <Collapse in={adminOpen} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            <ListItem button component={Link} to="/groups" sx={{ pl: 4 }}>
              <ListItemText primary="Groups" primaryTypographyProps={{ fontSize: '0.9rem', color: 'text.secondary' }} />
            </ListItem>
            <ListItem button component={Link} to="/userManagement" sx={{ pl: 4 }}>
              <ListItemText primary="User Management" primaryTypographyProps={{ fontSize: '0.9rem', color: 'text.secondary' }} />
            </ListItem>
            <ListItem button component={Link} to="/admin" sx={{ pl: 4 }}>
              <ListItemText primary="Tasks" primaryTypographyProps={{ fontSize: '0.9rem', color: 'text.secondary' }} />
            </ListItem>
            <ListItem button component={Link} to="/userDetails" sx={{ pl: 4 }}>
              <ListItemText primary="User Details" primaryTypographyProps={{ fontSize: '0.9rem', color: 'text.secondary' }} />
            </ListItem>
          </List>
        </Collapse>
        <ListItem button onClick={handleExportClick}>
          <ListItemText primary="Export" />
          {exportOpen ? <ExpandLess /> : <ExpandMore />}
        </ListItem>
        <Collapse in={exportOpen} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            <ListItem button onClick={handleExportFull} sx={{ pl: 4 }}>
              <ListItemText primary="Export Full Dataset" primaryTypographyProps={{ fontSize: '0.9rem', color: 'text.secondary' }} />
            </ListItem>
            <ListItem button onClick={handleExportFiltered} sx={{ pl: 4 }}>
              <ListItemText primary="Export Filtered Dataset" primaryTypographyProps={{ fontSize: '0.9rem', color: 'text.secondary' }} />
            </ListItem>
          </List>
        </Collapse>
        <ListItem button onClick={handleLogout}>
          <ListItemText primary="Logout" />
        </ListItem>
      </List>
    </Box>
  );
};

export default Menu;
