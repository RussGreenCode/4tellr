// src/components/DateSelect.js
import React from 'react';
import { TextField, IconButton, Box } from '@mui/material';
import { ArrowLeft, ArrowRight } from '@mui/icons-material';
import '../styles/DateSelect.css';

const DateSelect = ({ selectedDate, setSelectedDate }) => {
  const handleDateChange = (event) => {
    setSelectedDate(event.target.value);
  };

  const changeDateByDays = (days) => {
    const currentDate = new Date(selectedDate);
    console.log(currentDate);
    currentDate.setDate(currentDate.getDate() + days);
    setSelectedDate(currentDate.toISOString().split('T')[0]);
  };

  return (
    <Box display="flex" alignItems="center" className="date-select">
      <IconButton onClick={() => changeDateByDays(-1)}>
        <ArrowLeft />
      </IconButton>
      <TextField
        type="date"
        value={selectedDate}
        onChange={handleDateChange}
        variant="outlined"
        size="small"
        className="date-input"
      />
      <IconButton onClick={() => changeDateByDays(1)}>
        <ArrowRight />
      </IconButton>
    </Box>
  );
};

export default DateSelect;
