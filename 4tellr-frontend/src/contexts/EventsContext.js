import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';
import CalculateMettics from '../metrics/CalculateMetrics'
import CategoriseProcesses from '../utils/CategoriseProcesses'
import config from '../config';

export const EventsContext = createContext();

export const EventsProvider = ({ children }) => {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [favouriteFilteredEvents, setFavouriteFilteredEvents] = useState([])
  const [loading, setLoading] = useState(true);
  const today = new Date().toISOString().split('T')[0];
  const [businessDate, setBusinessDate] = useState(today); // Default date
  const [groupList, setGroupList] = useState({});
  const [searchEventCriteria, setSearchEventCriteria] = useState({}); // Initialize search criteria
  const [searchStatusCriteria, setSearchStatusCriteria] = useState({}); // Initialize search criteria
  const [searchApplicationCriteria, setSearchApplicationCriteria] = useState({}); // Initialize search criteria
  const [selectedEventList, setSelectedEventList] = useState([]);
  const [sortCriterion, setSortCriterion] = useState('EXP'); // Initialize search criteria
  const [selectedEvent, setSelectedEvent] = useState({}); // Initialize search criteria
  const [showLabels, setShowLabels] = useState(false);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [tabIndex, setTabIndex] = useState(0);
  const [searchGroupCriteria, setSearchGroupCriteria] = useState({})
  const [searchOutcomeCriteria, setSearchOutcomeCriteria] = useState({})
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
  const [justFinishedProcesses, setJustFinishedProcesses] = useState([])
  const [ongoingProcesses, setOngoingProcesses] = useState([])
  const [upcomingProcesses, setUpcomingProcesses] = useState([])
  const REFRESH_INTERVAL_SECONDS = 60;
  const [timeLeft, setTimeLeft] = useState(REFRESH_INTERVAL_SECONDS);

  const resetState = () => {
      setEvents([]);
      setFilteredEvents([]);
      setFavouriteFilteredEvents([]);
      setLoading(true);
      setBusinessDate(today); // Default date
      setGroupList({});
      setSearchEventCriteria({}); // Initialize search criteria
      setSearchStatusCriteria({}); // Initialize search criteria
      setSearchApplicationCriteria({}); // Initialize search criteria
      setSortCriterion('EXP'); // Initialize search criteria
      setSelectedEvent({}); // Initialize search criteria
      setShowLabels(false);
      setIsDrawerOpen(false);
      setTabIndex(0);
      setSearchGroupCriteria({});
      setSearchOutcomeCriteria({});
      setCurrentUser({}); // Initialize search criteria
      setMetrics({ summary: {}, eventStatus: {} });
      setFavouriteMetrics({ summary: {}, eventStatus: {} });
      setFilteredMetrics({ summary: {}, eventStatus: {} });
      setFavouriteGroups([]);
      setSelectedTypes({
        EVT: true,
        EXP: true,
        SLO: false,
        SLA: false
      });
    };

    const filterEvents = (events, groupCriteria, applicationCriteria, eventCriteria, statusCriteria, outcomeCriteria, selectedEventList) => {
      if (!Array.isArray(events)) {
        console.error('The events parameter is not an array.');
        return [];
      }

      return events.filter(event => {
        let matches = true;

        if (eventCriteria.eventName) {
          matches = matches && event.eventName.toLowerCase().includes(eventCriteria.eventName.toLowerCase());
        }

        if (statusCriteria.eventStatus) {
          matches = matches && event.eventStatus.toLowerCase().includes(statusCriteria.eventStatus.toLowerCase());
        }

        if (outcomeCriteria.eventOutcome) {
          matches = matches && event.plotStatus.toLowerCase().includes(outcomeCriteria.eventOutcome.toLowerCase());
        }

        if (groupCriteria.groupName) {
          matches = matches && event.groups && event.groups.includes(groupCriteria.groupName);
        }

        // Check against selectedEventList criteria
        if (selectedEventList && selectedEventList.length > 0) {
          const isSelected = selectedEventList.some(selectedEvent =>
            selectedEvent.event === event.eventName && selectedEvent.status === event.eventStatus
          );
          matches = matches && isSelected;
        }

        return matches;
      });
    };

  const fetchEvents = async (date) => {
    try {
      console.log('Fetching events for businessDate:', date);

      const app_prefix=`${config.baseUrl}/api/chart_data`

      const response = await axios.get(app_prefix, {
        params: { business_date: date }
      });

      // Add a method to process the events and add the groups that they exist in.
      const modifiedEvents = addGroupInformationToEvents(response.data, groupList)

      setEvents(modifiedEvents);
      const calculatedMetrics = CalculateMettics(modifiedEvents);
      setMetrics(calculatedMetrics);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching events:', error);
      setLoading(false);
    }
  };

  const addGroupInformationToEvents = (events, userFavouriteGroups) => {

    //Check that the user has some groups first
    if (!userFavouriteGroups || userFavouriteGroups.length === 0) {
      return events;
    }

    // Iterate through the event list to see if there is a match (an event may exist in more than one group)
    return events.map(event => {
      let eventGroups = [];

      userFavouriteGroups.forEach(group => {
        // Check if the event is part of the group's events
        if (group.events.includes(event.eventKey)) {
          eventGroups.push(group.group_name);
        }
      });

      // If there is a match, add the group names to the event
      if (eventGroups.length > 0) {
        return {
          ...event,
          groups: eventGroups,
        };
      }

      return event;
    });
  };

  const fetchUser = async (userEmail) => {
    try {
      console.log('Retrieving User:', currentUser.email);
      const response = await axios.get(`${config.baseUrl}/api/get_user`, {
        params: { email: userEmail }
      });
      setCurrentUser(response.data.user);
      setFavouriteGroups(response.data.groups);

    } catch (error) {
      console.error('Error refreshing user:', error)
    }
  };

  const fetchGroupList = async (date) => {
    try {
      console.log('Refreshing Group List:');
      const response = await axios.get(`${config.baseUrl}/api/get_groups`);
      setGroupList(response.data);
    } catch (error) {
      console.error('Error refreshing group list:', error)
    }

  };


  useEffect(() => {
    if (Object.keys(currentUser).length > 0) {
      fetchGroupList()
      fetchEvents(businessDate);

    }
  }, [businessDate, currentUser]);



  function filterFavouriteEvents(events) {
      //Check that the event belongs to a group
    return events.filter(event => Array.isArray(event.groups) && event.groups.length > 0);
  }

  useEffect(() => {
    // Filter events whenever events or search criteria change
    const updatedFilteredEvents = filterEvents(events, searchGroupCriteria, searchApplicationCriteria, searchEventCriteria, searchStatusCriteria, searchOutcomeCriteria, selectedEventList );
    setFilteredEvents(updatedFilteredEvents);

    const calculatedMetrics = CalculateMettics(updatedFilteredEvents);
    setFilteredMetrics(calculatedMetrics);

    const favouriteCalculatedMetrics = CalculateMettics( filterFavouriteEvents(events) )
    setFavouriteMetrics(favouriteCalculatedMetrics)

    //From the events we want to determine processes and then catagorise them
    CategoriseProcesses(events, setUpcomingProcesses, setOngoingProcesses, setJustFinishedProcesses)

  }, [events, searchGroupCriteria, searchApplicationCriteria, searchEventCriteria, searchStatusCriteria, searchOutcomeCriteria, selectedEventList, favouriteGroups]);

  const handleManualRefresh = () => {
    fetchEvents(businessDate);
  };

  return (
    <EventsContext.Provider value={{ events, filteredEvents, fetchEvents, loading, setBusinessDate, businessDate,
      setSearchStatusCriteria, searchStatusCriteria, setSearchApplicationCriteria, searchApplicationCriteria, setSearchEventCriteria, searchEventCriteria, selectedEvent, setSelectedEvent,
      tabIndex, setTabIndex, currentUser, setCurrentUser, fetchUser, sortCriterion, setSortCriterion, setSelectedTypes, selectedTypes,
      groupList, setGroupList, fetchGroupList, setSearchGroupCriteria, searchGroupCriteria, setShowLabels, showLabels, metrics,
      setSearchOutcomeCriteria, searchOutcomeCriteria, setSelectedEventList, timeLeft, handleManualRefresh, resetState,
      upcomingProcesses, ongoingProcesses, justFinishedProcesses,
      isDrawerOpen, setIsDrawerOpen, filteredMetrics, favouriteMetrics, favouriteGroups}}>
      {children}
    </EventsContext.Provider>
  );
};
