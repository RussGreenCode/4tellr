import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { format, startOfMonth, getDay, addDays } from 'date-fns';
import { EventsContext } from '../contexts/EventsContext';
import MicroBarChart from '../components/MicroBarChart';
import { useNavigate } from 'react-router-dom';
import config from '../config';

function CalendarSummary() {
  const { businessDate, setBusinessDate, fetchEvents } = useContext(EventsContext);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [data, setData] = useState({});
    const navigate = useNavigate();


  useEffect(() => {
    const fetchEventData = async () => {
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth() + 1; // Adjust for zero-based month index
      try {
        const response = await axios.get(`${config.baseUrl}/api/chart_data_monthly_summary?year=${year}&month=${month}`);
        setData(response.data);
      } catch (error) {
        console.error('Failed to fetch events', error);
        setData({});
      }
    };
    fetchEventData();
  }, [currentDate]);

  const handlePreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const handleDayClick = (date) => {
    const formattedDate = format(date, 'yyyy-MM-dd');
    setBusinessDate(formattedDate);
    navigate('/details');
  };

  const generateBarData = (filteredMetrics) => {
    const defaultMetrics = {
      BREACHED: 0,
      NOT_REACHED_EXP: 0,
      LATE: 0,
      MEETS_SLA: 0,
      MEETS_SLO: 0,
      ON_TIME: 0,
      NEW: 0
    };

    const metrics = {...defaultMetrics, ...filteredMetrics};

    const colorMapping = {
      BREACHED: 'darkred',
      NOT_REACHED_EXP: 'grey',
      LATE: 'red',
      MEETS_SLA: 'orange',
      MEETS_SLO: 'lightgreen',
      ON_TIME: 'darkgreen',
      NEW: 'blue'
    };

    return Object.keys(defaultMetrics).map(key => ({
      name: key.replace('_', ' '),
      value: metrics[key],
      color: colorMapping[key] || 'black',
      eventType: key
    }));
  };



  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  const startDay = getDay(startOfMonth(currentDate));
  const paddingDays = (startDay + 6) % 7; // Adjust for start of week on Monday

  const days = [];
  for (let i = 0; i < paddingDays; i++) {
    days.push(<div key={`padding-${i}`} style={{ visibility: 'hidden' }}></div>);
  }

  for (let i = 1; i <= daysInMonth; i++) {
    const date = addDays(new Date(currentDate.getFullYear(), currentDate.getMonth(), 1), i - 1);
    const formattedDate = format(date, 'EEE do');
    const dayData = data[i.toString()] ? generateBarData(data[i.toString()]) : generateBarData({});
    const totalEvents = data[i.toString()] ? data[i.toString()]['TOTAL_EVENTS'] : 'N/A';
    days.push(
      <div key={i} style={{ border: '1px solid #ccc', textAlign: 'center', height: '100%', padding: '2px' }}>
        <div style={{ height: '25%' }} onClick={() => handleDayClick(date)}>
          <h4 style={{ margin: 0, cursor: 'pointer' }}>{formattedDate} - Total: {totalEvents}</h4>
        </div>
        <div style={{ height: '75%' }}>
          <MicroBarChart data={dayData} handleClick={() => {}} />
        </div>
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginBottom: '20px' }}>
        <button onClick={handlePreviousMonth}>{"<"}</button>
        <h2 style={{ margin: '0 20px' }}>{format(currentDate, 'MMMM yyyy')}</h2>
        <button onClick={handleNextMonth}>{">"}</button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '5px', height: '50vh' }}>
        {days}
      </div>
    </div>
  );
}

export default CalendarSummary;
