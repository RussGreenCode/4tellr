import React, { useContext, useMemo, useEffect, useState } from 'react';
import { Box, Typography, Grid, Paper, Tabs, Tab } from '@mui/material';
import { EventsContext } from '../contexts/EventsContext';
import axios from 'axios';
import BarChartComponent from './BarChartComponent';
import PieChartComponent from './PieChartComponent';
import ScatterPlotComponent from './ScatterPlotComponent';
import EventDetailsComponent from './EventDetailsComponent';
import '../styles/AlertArea.css';

const AlertArea = () => {
  const { selectedEvent, setSearchCriteria, tabIndex, setTabIndex, filteredMetrics } = useContext(EventsContext);
  const [monthlyEvents, setMonthlyEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (selectedEvent && Object.keys(selectedEvent).length > 0) {
      setLoading(true);
      const fetchMonthlyEvents = async () => {
        try {
          const response = await axios.get('http://127.0.0.1:5000/api/event_details', {
            params: {
              eventName: selectedEvent.event,
              eventStatus: selectedEvent.status,
            },
          });
          setMonthlyEvents(response.data.events);
          setLoading(false);
        } catch (error) {
          console.error('Error fetching monthly events:', error);
          setLoading(false);
        }
      };
      fetchMonthlyEvents();
    }
  }, [selectedEvent]);

  const barData = [
    { name: 'On Time', value: filteredMetrics.eventStatus.ON_TIME, color: 'lightgreen', eventType: 'ON_TIME' },
    { name: 'Missed EXP', value: filteredMetrics.eventStatus.MEETS_SLO, color: 'darkgreen', eventType: 'MEETS_SLO' },
    { name: 'Missed SLO', value: filteredMetrics.eventStatus.MEETS_SLA, color: 'orange', eventType: 'MEETS_SLA' },
    { name: 'Missed SLA', value: filteredMetrics.eventStatus.LATE, color: 'red', eventType: 'LATE' }
  ];

  const handleBarClick = (data) => {
    setSearchCriteria({ eventStatus: data.eventType });
  };

  const handleTabChange = (event, newValue) => {
    setTabIndex(newValue);
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


  const monthlyData = useMemo(() => transformMonthlyEvents(monthlyEvents), [monthlyEvents]);

  const generate15MinuteTicks = (min, max) => {
    const ticks = [];
    for (let time = min; time <= max; time += 15 * 60) {
      ticks.push(time);
    }
    return ticks;
  };

  const minTime = Math.min(...monthlyData.map(d => d.eventTime));
  const maxTime = Math.max(...monthlyData.map(d => d.eventTime));
  const businessDates = monthlyData.map(d => d.businessDate);

  return (
    <Box>
      <Tabs value={tabIndex} onChange={handleTabChange}>
        <Tab label="Main Charts" />
        <Tab label="Event Details" />
        <Tab label="Event Trend" />
      </Tabs>

      {tabIndex === 0 && (
        <Grid container spacing={1}>
          <Grid item xs={12} md={6}>
            <Paper className="alert-paper" elevation={1}>
              <BarChartComponent data={barData} handleClick={handleBarClick} />
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper className="alert-paper" elevation={1}>
              <PieChartComponent data={barData} />
            </Paper>
          </Grid>
        </Grid>
      )}

      {tabIndex === 1 && (
        <Box>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <EventDetailsComponent event={selectedEvent} loading={loading} />
            </Grid>
          </Grid>
        </Box>
      )}

      {tabIndex === 2 && (
        <Box>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Paper className="alert-paper" elevation={1}>
                {selectedEvent && Object.keys(selectedEvent).length > 0 ? (
                  <ScatterPlotComponent
                    data={monthlyData}
                    minTime={minTime}
                    maxTime={maxTime}
                    businessDates={businessDates}
                    generateTicks={generate15MinuteTicks}
                  />
                ) : (
                  <Typography>No event selected</Typography>
                )}
              </Paper>
            </Grid>
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default AlertArea;
