import { useState, useEffect } from 'react';
import axios from 'axios';

const transformDataForChart = (events) => {
  console.log('Transforming events:', events); // Log events before transforming
  return events.map(event => ({
    primary: new Date(event.timestamp), // x-axis
    secondary: event.eventName,         // y-axis
    radius: 5,                          // size of the bubble
    originalDatum: event                // original event data for tooltip
  }));
};

export default function useEventData(businessDate) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('useEffect called with businessDate:', businessDate); // Log when useEffect is called

    const fetchEvents = async () => {
      console.log('Fetching events for date:', businessDate); // Log the API call
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/events', {
          params: { businessDate }
        });
        console.log('Fetched events:', response.data); // Log the response
        const transformedData = transformDataForChart(response.data);
        console.log('Transformed data:', transformedData);
        setData([{ label: 'Events', data: transformedData }]);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching events:', error);
        setError(error);
        setLoading(false);
      }
    };

    fetchEvents();
  }, [businessDate]);

  return { data, loading, error };
}
