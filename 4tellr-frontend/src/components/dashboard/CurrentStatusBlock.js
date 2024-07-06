// src/components/CurrentStatusBlock.js
import React, { useContext } from 'react';
import { Paper, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { EventsContext } from '../../contexts/EventsContext';

const CurrentStatusBlock = ({ label, value, plotStatus, className }) => {
  const navigate = useNavigate();
  const { setSearchOutcomeCriteria } = useContext(EventsContext);

  const handleClick = () => {
    setSearchOutcomeCriteria({ eventOutcome: plotStatus });
    navigate('/details');
  };

  return (
    <Paper className={`status-block ${className}`} onClick={handleClick} style={{ cursor: 'pointer' }}>
      <Typography variant="h6">{label}</Typography>
      <Typography variant="h4">{value}</Typography>
    </Paper>
  );
};

export default CurrentStatusBlock;
