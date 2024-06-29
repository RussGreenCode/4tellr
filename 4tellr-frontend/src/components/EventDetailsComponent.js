import React from 'react';
import { Typography, Paper } from '@mui/material';

const EventDetailsComponent = ({ event, loading, children }) => (
  <Paper className="alert-paper" elevation={1}>
    {event ? (
      <>
        <Typography variant="h6">Event Details</Typography>
        <Typography>Name: {event.event}</Typography>
        <Typography>Result: {event.result}</Typography>
        <Typography>Type: {event.type}</Typography>
        <Typography>Status: {event.status}</Typography>
        <Typography>Time: {new Date(event.time).toISOString()}</Typography>
        <Typography>Y-Coordinate: {event.yCoordinate}</Typography>
        {loading ? <Typography>Loading...</Typography> : children}
      </>
    ) : (
      <Typography>No event selected</Typography>
    )}
  </Paper>
);

export default EventDetailsComponent;
