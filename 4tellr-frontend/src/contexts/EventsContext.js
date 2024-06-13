import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

export const EventsContext = createContext();

export const EventsProvider = ({ children }) => {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [businessDate, setBusinessDate] = useState('2024-05-27'); // Default date
  const [searchCriteria, setSearchCriteria] = useState({}); // Initialize search criteria
  const [selectedEvent, setSelectedEvent] = useState({}); // Initialize search criteria
  const [tabIndex, setTabIndex] = useState(0);

  const filterEvents = (events, criteria) => {
    // Example filtering logic based on search criteria
    return events.filter(event => {
      let matches = true;
      if (criteria.eventType) {
        matches = matches && event.type === criteria.eventType;
      }
      if (criteria.eventStatus) {
        matches = matches && event.outcomeStatus === criteria.eventStatus;
      }
      if (criteria.eventKey) {
        matches = matches && event.eventKey.toLowerCase().includes(criteria.eventKey.toLowerCase());
      }
      // Add more filtering conditions here as needed
      return matches;
    });
  };

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

  useEffect(() => {
    // Filter events whenever events or search criteria change
    setFilteredEvents(filterEvents(events, searchCriteria));
    console.log('Filtered events:', filteredEvents);
  }, [events, searchCriteria]);

  return (
    <EventsContext.Provider value={{ events, filteredEvents, fetchEvents, loading, setBusinessDate, businessDate,  setSearchCriteria, selectedEvent, setSelectedEvent, tabIndex, setTabIndex}}>
      {children}
    </EventsContext.Provider>
  );
};
