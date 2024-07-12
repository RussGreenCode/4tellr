import React, { useContext } from 'react';
import { CircularProgress, IconButton, Box } from '@mui/material';
import { EventsContext } from '../contexts/EventsContext';

const CircularTimer = () => {
  const { timeLeft, handleManualRefresh } = useContext(EventsContext);
  const progress = (timeLeft / parseInt(60, 10)) * 100;

  return (
    <Box position="relative" display="inline-flex">
      <CircularProgress variant="determinate" value={progress} />
      <Box
        top={0}
        left={0}
        bottom={0}
        right={0}
        position="absolute"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <IconButton onClick={handleManualRefresh}>
          <Box position="absolute" display="flex" alignItems="center" justifyContent="center">
            {Math.ceil(timeLeft)}
          </Box>
        </IconButton>
      </Box>
    </Box>
  );
};

export default CircularTimer;
