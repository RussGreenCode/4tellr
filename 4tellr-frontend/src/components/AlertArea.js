import React, { useContext, useMemo, useEffect, useState } from 'react';
import { Box, Typography, Grid, Paper, Tabs, Tab } from '@mui/material';
import { PieChart, Pie, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ScatterChart, Scatter, CartesianGrid, Legend } from 'recharts';
import { EventsContext } from '../contexts/EventsContext';
import axios from 'axios';
import '../styles/AlertArea.css';


const formatTime = (tick) => {
  const totalMinutes = Math.floor(tick / 60);
  const minutes = totalMinutes % 60;
  const hours = Math.floor(totalMinutes / 60);
  return `${hours}:${minutes.toString().padStart(2, '0')}`;
};

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const { eventTime, businessDate} = payload[0].payload;
    return (
      <div className="custom-tooltip">
        <p className="intro">{`Date: ${businessDate}`}</p>
        <p className="intro">{`Time: ${formatTime(eventTime)}`}</p>
      </div>
    );
  }
  return null;
};

const AlertArea = () => {
  const { filteredEvents, selectedEvent, setSearchCriteria, tabIndex, setTabIndex, filteredMetrics } = useContext(EventsContext);
  const [monthlyEvents, setMonthlyEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch monthly events for the selected event
  useEffect(() => {
    if (selectedEvent) {
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


  // Data for bar chart
  const barData = [
    { name: 'On Time', value: filteredMetrics.eventStatus.ON_TIME, color: 'lightgreen', eventType: 'ON_TIME' },
    { name: 'Missed EXP', value: filteredMetrics.eventStatus.MEETS_SLO, color: 'darkgreen', eventType: 'MEETS_SLO' },
    { name: 'Missed SLO', value: filteredMetrics.eventStatus.MEETS_SLA, color: 'orange', eventType: 'MEETS_SLA' },
    { name: 'Missed SLA', value: filteredMetrics.eventStatus.LATE, color: 'red', eventType: 'LATE' }
  ];

  // Handle bar click to set search criteria
  const handleBarClick = (data) => {
    setSearchCriteria({ eventStatus: data.eventType });
  };

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabIndex(newValue);
  };

  // Transform monthly events data for scatter plot
  const transformMonthlyEvents = (events) => {
    return events.map(event => ({
      ...event,
      businessDate: new Date(event.businessDate).getTime(),
      eventTime: new Date(event.eventTime).getUTCHours() * 3600 + new Date(event.eventTime).getUTCMinutes() * 60 + new Date(event.eventTime).getUTCSeconds()
    }));
  };

  const monthlyData = useMemo(() => transformMonthlyEvents(monthlyEvents), [monthlyEvents]);

  const generate15MinuteTicks = (min, max) => {
    const ticks = [];
    const start = min
    const end = max
    for (let time = start; time <= end; time += 5 * 60) {
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
      </Tabs>

      {tabIndex === 0 && (
        <Grid container spacing={1}>
          <Grid item xs={12} md={6}>
            <Paper className="alert-paper" elevation={1}>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={barData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" onClick={handleBarClick}>
                    {barData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper className="alert-paper" elevation={1}>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={barData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                    {barData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      )}

      {tabIndex === 1 && (
        <Box>
          {(selectedEvent && Object.keys(selectedEvent).length > 0) ? (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Paper className="alert-paper" elevation={1}>
                  <Typography variant="h6">Event Details</Typography>
                  <Typography>Name: {selectedEvent.event}</Typography>
                  <Typography>Result: {selectedEvent.result}</Typography>
                  <Typography>Type: {selectedEvent.type}</Typography>
                  <Typography>Status: {selectedEvent.status}</Typography>
                  <Typography>Time: {new Date(selectedEvent.time).toISOString()}</Typography>
                  <Typography>Y-Coordinate: {selectedEvent.yCoordinate}</Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper className="alert-paper" elevation={1}>
                  {loading ? (
                    <Typography>Loading...</Typography>
                  ) : (
                    <ResponsiveContainer width="100%" height={250}>
                      <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid />
                        <YAxis
                          type="number"
                          dataKey="eventTime"
                          name="Event Time"
                          tickFormatter={(tick) => {
                            const totalMinutes = Math.floor(tick / 60);
                            const minutes = totalMinutes % 60;
                            const hours = Math.floor(totalMinutes / 60);
                            return `${hours}:${minutes.toString().padStart(2, '0')}`;
                          }}
                          domain={[minTime, maxTime]}
                          ticks={generate15MinuteTicks(minTime, maxTime)}
                        />
                        <XAxis
                          type="number"
                          dataKey="businessDate"
                          name="Business Date"
                          tickFormatter={(tick) => new Date(tick).toISOString().substr(0, 10)}
                          domain={[
                            dataMin => Math.min(...businessDates),
                            dataMax => Math.max(...businessDates)
                          ]}
                          ticks={businessDates}
                        />

                        <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
                        <Legend />
                        <Scatter name="Event Time" data={monthlyData} fill="#8884d8" />
                      </ScatterChart>
                    </ResponsiveContainer>
                  )}
                </Paper>
              </Grid>
            </Grid>
          ) : (
            <Paper className="alert-paper" elevation={1}>
              <Typography>No event selected</Typography>
            </Paper>
          )}
        </Box>
      )}
    </Box>
  );
};

export default AlertArea;
