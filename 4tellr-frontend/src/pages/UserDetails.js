// src/pages/UserDetails.js
import React, { useContext } from 'react';
import { EventsContext } from '../contexts/EventsContext';
import { Typography, List, ListItem, ListItemText, Box } from '@mui/material';
import config from '../config';

const UserDetails = () => {
  const { currentUser } = useContext(EventsContext);

  if (!currentUser) {
    return <Typography variant="h6">No user details available.</Typography>;
  }

  const { email, favourite_groups } = currentUser;

  return (
    <Box p={2}>
      <Typography variant="h4" gutterBottom>
        User Details
      </Typography>
      <List>
        <ListItem>
          <ListItemText primary="Email" secondary={email} />
        </ListItem>
        <ListItem>
          <ListItemText primary="Favourite Groups" />
          <List>
            {favourite_groups && favourite_groups.length > 0 ? (
              favourite_groups.map((group, index) => (
                <ListItem key={index}>
                  <ListItemText secondary={group} />
                </ListItem>
              ))
            ) : (
              <ListItem>
                <ListItemText secondary="No favorite groups available" />
              </ListItem>
            )}
          </List>
        </ListItem>
      </List>
    </Box>
  );
};

export default UserDetails;
