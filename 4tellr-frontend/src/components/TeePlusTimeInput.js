// src/components/TimeInput.js
import React, { useState, useEffect } from 'react';
import { Box, IconButton, TextField, Typography, Button } from '@mui/material';
import { ArrowDropUp, ArrowDropDown } from '@mui/icons-material';
import {DateTimeUtils} from "../utils/DateTimeUtils";

const TeePlusTimeInput = ({ label, value, onChange, fixedWidth = 600 }) => {
  const [days, setDays] = useState(1);
  const [hours, setHours] = useState(0);
  const [minutes, setMinutes] = useState(0);
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    if (value) {
      const {days, hours, minutes, seconds} = DateTimeUtils.parseTPlusTime(value)

      setDays(days);
      setHours(hours);
      setMinutes(minutes);
      setSeconds(seconds);
    }
  }, [value]);

  const handleIncrement = (unit) => {
    switch (unit) {
      case 'days':
        setDays(days + 1);
        break;
      case 'hours':
        setHours((hours + 1) % 24);
        break;
      case 'minutes':
        setMinutes((minutes + 1) % 60);
        break;
      case 'seconds':
        setSeconds((seconds + 1) % 60);
        break;
      default:
        break;
    }
  };

  const handleDecrement = (unit) => {
    switch (unit) {
      case 'days':
        setDays(days > 0 ? days - 1 : 5);
        break;
      case 'hours':
        setHours(hours > 0 ? hours - 1 : 23);
        break;
      case 'minutes':
        setMinutes(minutes > 0 ? minutes - 1 : 59);
        break;
      case 'seconds':
        setSeconds(seconds > 0 ? seconds - 1 : 59);
        break;
      default:
        break;
    }
  };

  const formatTime = () => {
    return `T+${days} ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleSubmit = () => {
    const newTPlusTime = DateTimeUtils.formatDifferenceFromStrings(days, hours, minutes, seconds)
    onChange(newTPlusTime);

    console.info('label', label);
    console.info('newTPlusTime', newTPlusTime);
  };

  return (
    <Box display="flex" alignItems="center" width={fixedWidth}>
      <Typography variant="h8" style={{ marginRight: '16px', minWidth: '160px' }}>{label}</Typography>
      <Typography variant="h8" style={{ marginRight: '16px', minWidth: '120px' }}>{formatTime()}</Typography>
      <Box display="flex" flexDirection="column" alignItems="center" style={{ marginRight: '5px', marginLeft: '20px' }}>
        <TextField label="Days" value={days.toString().padStart(2, '0')} variant="outlined" size="small" style={{ width: '80px', marginRight: '0px' }} />
      </Box>
      <Box display="flex" flexDirection="column" alignItems="center">
        <Box display="flex" justifyContent="space-between" width="100%">
          <IconButton onClick={() => handleIncrement('days')}>
            <ArrowDropUp />
          </IconButton>
        </Box>
        <Box>
          <IconButton onClick={() => handleDecrement('days')}>
            <ArrowDropDown />
          </IconButton>
        </Box>
      </Box>
      <Box display="flex" flexDirection="column" alignItems="center" style={{ marginRight: '5px', marginLeft: '20px' }}>
        <TextField label="Hours" value={hours.toString().padStart(2, '0')} variant="outlined" size="small" style={{ width: '80px', marginRight: '0px' }} />
      </Box>
      <Box display="flex" flexDirection="column" alignItems="center">
        <Box display="flex" justifyContent="space-between" width="100%">
          <IconButton onClick={() => handleIncrement('hours')}>
            <ArrowDropUp />
          </IconButton>
        </Box>
        <Box>
          <IconButton onClick={() => handleDecrement('hours')}>
            <ArrowDropDown />
          </IconButton>
        </Box>
      </Box>
      <Box display="flex" flexDirection="column" alignItems="center" style={{ marginRight: '5px', marginLeft: '20px' }}>
        <TextField label="Minutes" value={minutes.toString().padStart(2, '0')} variant="outlined" size="small" style={{ width: '80px', marginRight: '0px' }} />
      </Box>
      <Box display="flex" flexDirection="column" alignItems="center">
        <Box display="flex" justifyContent="space-between" width="100%">
          <IconButton onClick={() => handleIncrement('minutes')}>
            <ArrowDropUp />
          </IconButton>
        </Box>
        <Box>
          <IconButton onClick={() => handleDecrement('minutes')}>
            <ArrowDropDown />
          </IconButton>
        </Box>
      </Box>
      <Box display="flex" flexDirection="column" alignItems="center" style={{ marginRight: '5px', marginLeft: '20px' }}>
        <TextField label="Seconds" value={seconds.toString().padStart(2, '0')} variant="outlined" size="small" style={{ width: '80px', marginRight: '0px' }} />
      </Box>
      <Box display="flex" flexDirection="column" alignItems="center">
        <Box display="flex" justifyContent="space-between" width="100%">
          <IconButton onClick={() => handleIncrement('seconds')}>
            <ArrowDropUp />
          </IconButton>
        </Box>
        <Box>
          <IconButton onClick={() => handleDecrement('seconds')}>
            <ArrowDropDown />
          </IconButton>
        </Box>
      </Box>
      <Button variant="contained" color="primary" onClick={handleSubmit} style={{ marginLeft: '30px' }}>
        Submit
      </Button>
    </Box>
  );
};

export default TeePlusTimeInput;
