import React, { useContext } from 'react';
import ChartComponent from './ChartComponent';
import { EventsContext } from '../contexts/EventsContext';
import { transformEventsForChart } from '../utils/transformEvents';
import { Box } from '@mui/material';



const EventFetcher = () => {
  const { filteredEvents, loading } = useContext(EventsContext);

  if (loading) {
    return <div>Loading...</div>;
  }

  const data = transformEventsForChart(filteredEvents);

  return (
    <Box>
      <ChartComponent data={[{ label: 'Events', data }]} />
    </Box>
  );
};

export default EventFetcher;
