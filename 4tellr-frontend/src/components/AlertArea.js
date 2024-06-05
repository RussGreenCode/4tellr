import React, { useContext, useMemo } from 'react';
import { Box, Typography, Grid, Paper } from '@mui/material';
import { PieChart, Pie, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { EventsContext } from '../contexts/EventsContext';
import '../styles/AlertArea.css';

const AlertArea = () => {
  const { filteredEvents, setSearchCriteria } = useContext(EventsContext);

  // Calculate metrics
  const metrics = useMemo(() => {
    const totalEvents = filteredEvents.length;
    const expectations = filteredEvents.filter(event => event.type === 'EXP');
    const completed = expectations.filter(event => event.outcomeStatus === 'ON_TIME' || event.outcomeStatus === 'MEETS_SLO' || event.outcomeStatus === 'MEETS_SLA').length;
    const onTime = expectations.filter(event => event.outcomeStatus === 'ON_TIME').length;
    const missedExpectations = expectations.filter(event => event.outcomeStatus === 'MEETS_SLO').length;
    const missedSLOs = expectations.filter(event => event.outcomeStatus === 'MEETS_SLA').length;
    const errors = expectations.filter(event => event.outcomeStatus === 'ERROR').length;

    return {
      totalEvents,
      expectations: expectations.length,
      completed,
      errors,
      missedExpectations,
      missedSLOs,
      onTime
    };
  }, [filteredEvents]);

  // Data for bar chart
  const barData = [
    { name: 'On Time', value: metrics.onTime, color: 'lightgreen', eventType: 'ON_TIME' },
    { name: 'Missed Expectations', value: metrics.missedExpectations, color: 'darkgreen', eventType: 'MEETS_SLO' },
    { name: 'Missed SLO', value: metrics.missedSLOs, color: 'orange', eventType: 'MEETS_SLA' },
    { name: 'Errors', value: metrics.errors, color: 'red', eventType: 'ERROR' }
  ];

  // Handle bar click to set search criteria
  const handleBarClick = (data) => {
    setSearchCriteria({ eventStatus: data.eventType });
  };

  return (
    <Grid container spacing={1}>
      <Grid item xs={12} md={6}>
        <Paper className="alert-paper" elevation={1}>
          <ResponsiveContainer width="100%" height={300}>
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
          <ResponsiveContainer width="100%" height={300}>
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
  );
};

export default AlertArea;
