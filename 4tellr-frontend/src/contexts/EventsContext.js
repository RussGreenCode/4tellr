import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

export const EventsContext = createContext();

export const EventsProvider = ({ children }) => {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [businessDate, setBusinessDate] = useState('2024-05-27'); // Default date
  const [groupList, setGroupList] = useState({});
  const [searchEventCriteria, setSearchEventCriteria] = useState({}); // Initialize search criteria
  const [searchStatusCriteria, setSearchStatusCriteria] = useState({}); // Initialize search criteria
  const [searchApplicationCriteria, setSearchApplicationCriteria] = useState({}); // Initialize search criteria
  const [sortCriterion, setSortCriterion] = useState('EXP'); // Initialize search criteria
  const [selectedEvent, setSelectedEvent] = useState({}); // Initialize search criteria
  const [showLabels, setShowLabels] = useState(false);
  const [tabIndex, setTabIndex] = useState(0);
  const [searchGroupCriteria, setSearchGroupCriteria] = useState({})
  const [currentUser, setCurrentUser] = useState({}); // Initialize search criteria
  const [selectedTypes, setSelectedTypes] = useState({
    EVT: true,
    EXP: true,
    SLO: false,
    SLA: false
  });


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

  const fetchUser = async (date) => {
    try {
      console.log('Refreshing User:', currentUser.email);
      const response = await axios.get('http://127.0.0.1:5000/api/get_user', {
        params: { email: currentUser.email }
      });
      setCurrentUser(response.data);
    } catch (error) {
      console.error('Error refreshing user:', error)
    }
  };

  const fetchGroupList = async (date) => {
    try {
      console.log('Refreshing Group List:');
      const response = await axios.get('http://127.0.0.1:5000/api/get_groups');
      setGroupList(response.data);
    } catch (error) {
      console.error('Error refreshing group list:', error)
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
    setFilteredEvents(filterEvents(events, searchEventCriteria));
    console.log('Filtered events:', filteredEvents);
  }, [events, searchEventCriteria]);

  useEffect(() => {
    fetchGroupList()
  }, []);

  return (
    <EventsContext.Provider value={{ events, filteredEvents, fetchEvents, loading, setBusinessDate, businessDate,
      setSearchStatusCriteria, setSearchApplicationCriteria, setSearchEventCriteria, selectedEvent, setSelectedEvent,
      tabIndex, setTabIndex, currentUser, setCurrentUser, fetchUser, sortCriterion, setSelectedTypes, selectedTypes,
      groupList, fetchGroupList, setSearchGroupCriteria, setShowLabels, showLabels}}>
      {children}
    </EventsContext.Provider>
  );
};
