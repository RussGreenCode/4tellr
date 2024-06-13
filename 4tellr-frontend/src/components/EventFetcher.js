import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import ChartComponent from './ChartComponent';
import { EventsContext } from '../contexts/EventsContext';
import moment from 'moment';
import { Box, TextField, MenuItem, Select, FormControl, InputLabel } from '@mui/material';



const EventFetcher = ({ businessDate }) => {
  const { filteredEvents, loading } = useContext(EventsContext);
  const [sortCriterion, setSortCriterion] = useState('EXP'); // Default sorting criterion

  const transformDataForChart = (filteredEvents) => {
    const currentTime = new Date();
    return filteredEvents.map(event => {
      const eventTime = moment(event.TimeValue).toDate();

      let color;
      if (event.outcomeStatus !== 'N/A') {
        color = event.outcomeStatus === 'NEW' ? 'white'
              : event.outcomeStatus === 'ON_TIME' ? 'lightgreen'
              : event.outcomeStatus === 'MEETS_SLO' ? 'darkgreen'
              : event.outcomeStatus === 'MEETS_SLA' ? 'orange'
              : 'red';
      } else if (event.type === 'EXP') {
        color = currentTime < eventTime ? 'grey' : 'red';
      }


      return {
        type: event.type,
        time: eventTime.getTime(),
        event: event.eventName,
        status: event.eventStatus,
        size: 5,
        color,
        yCoordinate: event.eventKey,
        expectationTime: event.type === 'EXP' ? eventTime.getTime() : null // Add expectation time for sorting
      };
    });
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  const data = transformDataForChart(filteredEvents);

  console.log('Transformed data for chart:', data);

  return (
    <Box>
      <FormControl>
        <InputLabel id="sort-criterion-label">Sort By</InputLabel>
        <Select
          labelId="sort-criterion-label"
          id="sort-criterion"
          value={sortCriterion}
          onChange={(e) => setSortCriterion(e.target.value)}
        >
          <MenuItem value="EXP">Expectation Time</MenuItem>
          <MenuItem value="EVT">Event Time</MenuItem>
        </Select>
      </FormControl>
      <ChartComponent data={[{ label: 'Events', data }]} sortCriterion={sortCriterion} />
    </Box>
  );
};

export default EventFetcher;
