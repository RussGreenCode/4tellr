import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';
import CalculateMettics from '../metrics/CalculateMetrics'

export const EventsContext = createContext();

export const EventsProvider = ({ children }) => {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [favouriteFilteredEvents, setFavouriteFilteredEvents] = useState([])
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
  const [metrics, setMetrics] = useState({ summary: {}, eventStatus: {} });
  const [favouriteMetrics, setFavouriteMetrics] = useState({ summary: {}, eventStatus: {} });
  const [filteredMetrics, setFilteredMetrics] = useState({ summary: {}, eventStatus: {} });
  const [favouriteGroups, setFavouriteGroups] = useState([])
  const [selectedTypes, setSelectedTypes] = useState({
    EVT: true,
    EXP: true,
    SLO: false,
    SLA: false
  });


  const filterEvents = (events, groupCriteria, applicationCriteria, eventCriteria, statusCriteria) => {
    // Example filtering logic based on search criteria
    return events.filter(event => {
      let matches = true;

      if (eventCriteria.eventName) {
        matches = matches && event.eventName.toLowerCase().includes(eventCriteria.eventName.toLowerCase());
      }

      if (statusCriteria.eventStatus) {
        matches = matches && event.eventStatus.toLowerCase().includes(statusCriteria.eventStatus.toLowerCase());
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
      const calculatedMetrics = CalculateMettics(response.data);
      setMetrics(calculatedMetrics);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching events:', error);
      setLoading(false);
    }
  };

  const fetchUser = async (date) => {
    try {
      console.log('Retrieving User:', currentUser.email);
      const response = await axios.get('http://127.0.0.1:5000/api/get_user', {
        params: { email: currentUser.email }
      });
      setCurrentUser(response.data.user);
      setFavouriteGroups(response.data.groups)
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


    }, 600000); // Update every minute
    return () => clearInterval(interval);
  }, [businessDate]);

  function filterFavouriteEvents(events) {
    // Ensure favoriteGroups is an array
    if (!Array.isArray(favouriteGroups)) {
      console.error('favoriteGroups should be an array.');
      return events;
    }

    const favouriteEventList = [];

     // Extract favourite events from favouriteGroups
    favouriteGroups.forEach(group => {
      if (Array.isArray(group.events)) {
        favouriteEventList.push(...group.events);
      } else {
        favouriteEventList.push(group.events);
      }
    });

    // Filter the events by eventKey where it matches the favouriteEventList
    const filteredEvents = events.filter(event => favouriteEventList.includes(event.eventKey));


    return filteredEvents;

  }

  useEffect(() => {
    // Filter events whenever events or search criteria change
    const updatedFilteredEvents = filterEvents(events, searchGroupCriteria, searchApplicationCriteria, searchEventCriteria, searchStatusCriteria );
    setFilteredEvents(updatedFilteredEvents);

    const updatedFavouriteFilteredEvents = filterFavouriteEvents(events)
    setFavouriteFilteredEvents(updatedFavouriteFilteredEvents)

    const calculatedMetrics = CalculateMettics(updatedFilteredEvents);
    setFilteredMetrics(calculatedMetrics);
    
    const favouriteCalculatedMetrics = CalculateMettics(updatedFavouriteFilteredEvents)
    setFavouriteMetrics(favouriteCalculatedMetrics)
    console.log('Filtered events:', filteredEvents);

  }, [events, searchGroupCriteria, searchApplicationCriteria, searchEventCriteria, searchStatusCriteria, favouriteGroups]);

  useEffect(() => {
    fetchGroupList()
  }, []);



  return (
    <EventsContext.Provider value={{ events, filteredEvents, fetchEvents, loading, setBusinessDate, businessDate,
      setSearchStatusCriteria, searchStatusCriteria, setSearchApplicationCriteria, searchApplicationCriteria, setSearchEventCriteria, searchEventCriteria, selectedEvent, setSelectedEvent,
      tabIndex, setTabIndex, currentUser, setCurrentUser, fetchUser, sortCriterion, setSelectedTypes, selectedTypes,
      groupList, fetchGroupList, setSearchGroupCriteria, searchGroupCriteria, setShowLabels, showLabels, metrics, filteredMetrics, favouriteMetrics}}>
      {children}
    </EventsContext.Provider>
  );
};
