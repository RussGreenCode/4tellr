import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

export const EventsContext = createContext();

export const EventsProvider = ({ children }) => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [businessDate, setBusinessDate] = useState('2024-05-27'); // Default date

  const fetchEvents = async (date) => {
    try {
      console.log('Fetching events for businessDate:', date);
      const response = await axios.get('http://127.0.0.1:5000/api/chart_data', {
        params: { businessDate: date }
      });
      console.log('Fetched events response:', response.data);
      setEvents(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching events:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents(businessDate);
    const interval = setInterval(() => {
      fetchEvents(businessDate);
    }, 60000); // Update every minute
    return () => clearInterval(interval);
  }, [businessDate]);

  return (
    <EventsContext.Provider value={{ events, fetchEvents, loading, setBusinessDate, businessDate }}>
      {children}
    </EventsContext.Provider>
  );
};
