// src/components/TimeInput.js
import React, { useState, useEffect } from 'react';
import { Box, IconButton, TextField, Typography, Button } from '@mui/material';
import { ArrowDropUp, ArrowDropDown } from '@mui/icons-material';
import { DateTimeUtils } from '../utils/DateTimeUtils';

const TimeInput = ({ label, baseValue, value, onChange, fixedWidth = 600 }) => {
  const [hours, setHours] = useState(0);
  const [minutes, setMinutes] = useState(0);
  const [difference, setDifference] = useState('');
  const [valueDate, setValueDate] = useState(new Date());
  const [baseValueDate, setBaseValueDate] = useState(new Date());

  useEffect(() => {
    if (value && baseValue) {
      const baseValueDateCalc = DateTimeUtils.parseTPlusTime(baseValue);
      const valueDateCalc = value === 'undefined' ? baseValueDateCalc : DateTimeUtils.parseTPlusTime(value);

      setBaseValueDate(baseValueDateCalc);
      setValueDate(valueDateCalc);

      const timeDifference = DateTimeUtils.calculateTimeDifference(baseValueDateCalc, valueDateCalc);
      const formattedDifference = DateTimeUtils.formatDifference(timeDifference);

      const [diffHours, diffMinutes] = formattedDifference.split(':').map(Number);

      setDifference(formattedDifference);
      setHours(diffHours);
      setMinutes(diffMinutes);

      console.info('label', label);
      console.info('baseValue', baseValue);
      console.info('value', value);
      console.info('baseValueDateCalc', baseValueDateCalc);
      console.info('valueDateCalc', valueDateCalc);
      console.info('timeDifference', timeDifference);
      console.info('formattedDifference', formattedDifference);
      console.info('diffHours', diffHours);
      console.info('diffHours', diffMinutes);
    }
  }, [value, baseValue]);

  const handleIncrement = (unit) => {
    switch (unit) {
      case 'hours':
        setHours((hours + 1) % 24);
        break;
      case 'minutes':
        setMinutes((minutes + 1) % 60);
        break;
      default:
        break;
    }
  };

  const handleDecrement = (unit) => {
    switch (unit) {
      case 'hours':
        setHours(hours > 0 ? hours - 1 : 23);
        break;
      case 'minutes':
        setMinutes(minutes > 0 ? minutes - 1 : 59);
        break;
      default:
        break;
    }
  };

  const handleSubmit = () => {
    const newTPlusTime = DateTimeUtils.addTimeToTPlus(baseValue, hours, minutes);
    onChange(newTPlusTime);

    console.info('label', label);
    console.info('baseValue', baseValue);
    console.info('newTPlusTime', newTPlusTime);
  };

  const formatTime = () => {
    return `Exp + ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
  };

  return (
    <Box display="flex" alignItems="center" width={fixedWidth}>
      <Typography variant="h8" style={{ marginRight: '16px', minWidth: '160px' }}>{label}</Typography>
      <Typography variant="h8" style={{ marginRight: '16px', minWidth: '160px' }}>{value}</Typography>
      <Typography variant="h8" style={{ marginRight: '16px', minWidth: '120px' }}>{`${formatTime()}`}</Typography>
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
      <Button variant="contained" color="primary" onClick={handleSubmit} style={{ marginLeft: '30px' }}>
        Submit
      </Button>
    </Box>
  );
};

export default TimeInput;
