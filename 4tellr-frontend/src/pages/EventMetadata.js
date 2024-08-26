import React, { useState, useEffect, useMemo } from 'react';
import { Box, Typography, TextField, Button, Autocomplete, Tabs, Tab } from '@mui/material';
import axios from 'axios';
import MiniGanttChartD3 from '../components/MiniGanttChart';
import ScatterPlotComponent from "../components/ScatterPlotComponent";
import TimeInput from '../components/TimeInput';
import TeePlusTimeInput from '../components/TeePlusTimeInput';

const EventMetadata = () => {
  const [eventName, setEventName] = useState('');
  const [eventStatus, setEventStatus] = useState('');
  const [metadata, setMetadata] = useState({});
  const [events, setEvents] = useState([]);
  const [processes, setProcesses] = useState([]);
  const [selectedOccurrenceIndex, setSelectedOccurrenceIndex] = useState(0);
  const [expectationTime, setExpectationTime] = useState('');
  const [sloTime, setSloTime] = useState('');
  const [slaTime, setSlaTime] = useState('');
  const [dependencies, setDependencies] = useState([]);
  const [allSuccessEvents, setAllSuccessEvents] = useState([]);
  const [dependentEvents, setDependentEvents] = useState([]);
  const [eventMetadataList, setEventMetadataList] = useState([]);
  const [filteredEventMetadataList, setFilteredEventMetadataList] = useState([]);
  const [selectedMetadataId, setSelectedMetadataId] = useState('');

  useEffect(() => {
    fetchEventMetadataList();
  }, []);

  useEffect(() => {
    if (selectedMetadataId) {
      fetchMetadata();
    }
  }, [selectedMetadataId]);

  useEffect(() => {
    if (metadata.daily_occurrences && metadata.daily_occurrences.length > 0) {
      const selectedOccurrence = metadata.daily_occurrences[selectedOccurrenceIndex];
      setExpectationTime(selectedOccurrence.expectation.time);
      setSloTime(selectedOccurrence.slo.time);
      setSlaTime(selectedOccurrence.sla.time);
      fetchEventStats();
      fetchProcesses();
    }
  }, [metadata, selectedOccurrenceIndex]);

  const fetchEventMetadataList = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/event/event_metadata_list');
      if (response.data && response.data.length > 0) {
        setEventMetadataList(response.data);
        setFilteredEventMetadataList(response.data);
      } else {
        console.error('No event metadata found');
      }
    } catch (error) {
      console.error('Error fetching event metadata list:', error);
    }
  };

  const fetchMetadata = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:5000/api/event/get_event_metadata`, { params: { id: selectedMetadataId } });
      if (response.data) {
        setMetadata(response.data);
        setEventName(response.data.event_name);
        setEventStatus(response.data.event_status);
        // Initialize occurrence-related states
        if (response.data.daily_occurrences && response.data.daily_occurrences.length > 0) {
          setSelectedOccurrenceIndex(0); // Select the first occurrence by default
        }
        setDependencies(response.data.dependencies || []);
      } else {
        console.error('No metadata found for the selected ID ', selectedMetadataId);
      }
    } catch (error) {
      console.error('Error fetching metadata:', error);
    }
  };

  const fetchEventStats = async () => {

    const event_name = eventName
    const event_status = eventStatus

    try {
      if (Object.keys(metadata).length !== 0) {
        const response = await axios.get('http://127.0.0.1:5000/api/event_details', {
          params: {
            event_name: event_name,
            event_status: event_status,
          },
        });
        setEvents(response.data.events);
      }
    } catch (error) {
      console.error('Error fetching event stats:', error);
    }
  };

  const fetchProcesses = async () => {
    try {
      if (Object.keys(metadata).length !== 0) {
        const event_name = eventName
        const response = await axios.get(`http://127.0.0.1:5000/api/process/get_process_statistics`, { params: { event_name } });
        setProcesses(response.data);
      }
    } catch (error) {
      console.error('Error fetching processes:', error);
    }
  };

  const fetchAllSuccessEvents = async () => {
    try {
      if (metadata !== {}) {
        // Filter the events based on event_status being 'SUCCESS'
        const successEvents = metadata.filter(event => event.event_status === 'SUCCESS');
        setAllSuccessEvents(successEvents);
      }
    } catch (error) {
      console.error('Error fetching all success events:', error);
    }
  }

  const handleSave = async () => {
    try {
      const updatedOccurrences = metadata.daily_occurrences.map((occurrence, index) => {
        if (index === selectedOccurrenceIndex) {
          return {
            ...occurrence,
            expectation: { ...occurrence.expectation, time: expectationTime },
            slo: { ...occurrence.slo, time: sloTime },
            sla: { ...occurrence.sla, time: slaTime }
          };
        }
        return occurrence;
      });

      const response = await axios.put(`http://127.0.0.1:5000/api/event/event_metadata`, {
        id: selectedMetadataId,
        event_name: eventName,
        event_status: eventStatus,
        daily_occurrences: updatedOccurrences,
        dependencies,
      });

      console.log('Save response:', response.data);
    } catch (error) {
      console.error('Error saving metadata:', error);
    }
  };

  const handleMetadataSelect = (event, value) => {
    setSelectedMetadataId(value ? value._id : '');
  };

  const handleTabChange = (event, newValue) => {
    setSelectedOccurrenceIndex(newValue);
  };

  const transformMonthlyEvents = (events) => {
    return events.map(event => {
      const businessDate = new Date(event.businessDate);
      const eventTime = new Date(event.eventTime);

      // Ensure both dates are in UTC
      const businessDateUTC = Date.UTC(businessDate.getUTCFullYear(), businessDate.getUTCMonth(), businessDate.getUTCDate());
      const eventTimeUTC = Date.UTC(eventTime.getUTCFullYear(), eventTime.getUTCMonth(), eventTime.getUTCDate(), eventTime.getUTCHours(), eventTime.getUTCMinutes(), eventTime.getUTCSeconds());

      // Calculate the difference in milliseconds
      const timeDifferenceInMillis = eventTimeUTC - businessDateUTC;

      // Convert milliseconds to seconds
      const timeDifferenceInSeconds = timeDifferenceInMillis / 1000;

      return {
        ...event,
        businessDate: businessDateUTC,
        eventTime: timeDifferenceInSeconds
      };
    });
  };

  const monthlyData = useMemo(() => transformMonthlyEvents(events), [events]);

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>Event Metadata</Typography>
      <Box mb={3}>
        <Autocomplete
          options={filteredEventMetadataList}
          getOptionLabel={(option) => `${option.event_name} - ${option.event_status}`}
          onChange={handleMetadataSelect}
          renderInput={(params) => <TextField {...params} label="Search Event Metadata" variant="outlined" />}
        />
      </Box>
      {selectedMetadataId && (
        <Box>
          <Box display="flex" justifyContent="space-between">
            <Box width="50%">
              <Typography variant="h6" mt={3}>Event Statistics</Typography>
              <ScatterPlotComponent
                data={monthlyData}
                width={700}
                height={400}
                textSize={10}
              />
            </Box>
            <Box width="50%">
              <Typography variant="h6" mt={3}>Gantt Chart of Processes</Typography>
              <MiniGanttChartD3 data={processes} width={700} height={300} textSize={12} />
            </Box>
          </Box>
          <Box mt={3}>
            <Typography variant="h6">Edit Event Metadata</Typography>
            <Tabs value={selectedOccurrenceIndex} onChange={handleTabChange} aria-label="occurrence tabs">
              {metadata.daily_occurrences && metadata.daily_occurrences.map((occurrence, index) => (
                <Tab key={index} label={`Occurrence ${index + 1}`} />
              ))}
            </Tabs>
            {metadata.daily_occurrences && metadata.daily_occurrences.length > 0 && (
              <Box mt={2}>
                <TeePlusTimeInput
                  label="Expectation Time"
                  value={expectationTime}
                  onChange={setExpectationTime}
                />
                <TimeInput
                  label="SLO Time"
                  baseValue={expectationTime}
                  value={sloTime}
                  onChange={setSloTime}
                />
                <TimeInput
                  label="SLA Time"
                  baseValue={expectationTime}
                  value={slaTime}
                  onChange={setSlaTime}
                />
                <Button variant="contained" color="primary" onClick={handleSave}>
                  Save
                </Button>
              </Box>
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default EventMetadata;
