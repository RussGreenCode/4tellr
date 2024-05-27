import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ChartComponent from './ChartComponent';

const EventFetcher = ({ businessDate }) => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.error('useEffect being called:');

    const businessDate = '2024-05-24';
    const fetchEvents = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/events', {
          params: { businessDate }
        });
        setEvents(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching events:', error);
        setLoading(false);
      }
    };

    fetchEvents();
  }, [businessDate]);

  const transformDataForChart = (events) => {
    return events.map(event => ({
      primary: new Date(event.timestamp), // x-axis
      secondary: event.eventName,         // y-axis
      radius: 5,                          // size of the bubble
      originalDatum: event                // original event data for tooltip
    }));
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  const data = transformDataForChart(events);

  console.log('Transformed data for chart:', data);

  return (
    <ChartComponent data={[{ label: 'Events', data }]} />
  );
};

export default EventFetcher;
