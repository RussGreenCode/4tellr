import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ChartComponent from './ChartComponent';
import moment from 'moment';

const EventFetcher = ({ businessDate }) => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('useEffect called with businessDate:', businessDate);

    const fetchEvents = async () => {
      try {
        console.log('Fetching events for businessDate:', businessDate);
        const response = await axios.get('http://127.0.0.1:5000/api/chart_data', {
          params: { businessDate }
        });
        console.log('Fetched events response:', response.data);
        setEvents(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching events:', error);
        setLoading(false);
      }
    };

    fetchEvents();
  }, [businessDate]);

  const transformDataForChart = (events) => {
    const currentTime = new Date();
    return events.map(event => {
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
        size: 5,
        color,
        yCoordinate: event.eventKey
      };
    });
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  const data = transformDataForChart(events);

  console.log('Transformed data for chart:', data);

  return (
    <ChartComponent data={[{ label: 'Events', data }]} />
  );
};

export default EventFetcher;
