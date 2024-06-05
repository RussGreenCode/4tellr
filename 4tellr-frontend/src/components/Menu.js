import React, { useContext } from 'react';
import { List, ListItem, ListItemText, Box, ListSubheader } from '@mui/material';
import { Link } from 'react-router-dom';
import { EventsContext } from '../contexts/EventsContext';
import '../styles/App.css';
import { exportToCSV } from '../utils/exportUtils';

const menuItems = [
  { name: 'Overview', link: '/' },
  { name: 'Metrics', link: '/metrics' },
  { name: 'Settings', link: '/settings' },
  { name: 'Admin', link: '/admin' },
];

const Menu = () => {
  const { events, filteredEvents } = useContext(EventsContext);

  const handleExportFull = () => {
    exportToCSV(events, 'full_dataset.csv');
  };

  const handleExportFiltered = () => {
    exportToCSV(filteredEvents, 'filtered_dataset.csv');
  };

  return (
    <Box>
      <List>
        {menuItems.map((item, index) => (
          <ListItem button component={Link} to={item.link} key={index}>
            <ListItemText primary={item.name} />
          </ListItem>
        ))}
        <ListSubheader>Export</ListSubheader>
        <ListItem button onClick={handleExportFull}>
          <ListItemText primary="Export Full Dataset" />
        </ListItem>
        <ListItem button onClick={handleExportFiltered}>
          <ListItemText primary="Export Filtered Dataset" />
        </ListItem>
      </List>
    </Box>
  );
};

export default Menu;
