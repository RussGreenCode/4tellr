// src/components/Menu.js
import React from 'react';
import { List, ListItem, ListItemText, Box } from '@mui/material';
import { Link } from 'react-router-dom';
import '../styles/App.css';

const menuItems = [
  { name: 'Overview', link: '/' },
  { name: 'Metrics', link: '/metrics' },
  { name: 'Settings', link: '/settings' },
  { name: 'Admin', link: '/admin' },
];

const Menu = () => (
  <Box>
    <List>
      {menuItems.map((item, index) => (
        <ListItem button component={Link} to={item.link} key={index}>
          <ListItemText primary={item.name} />
        </ListItem>
      ))}
    </List>
  </Box>
);

export default Menu;
