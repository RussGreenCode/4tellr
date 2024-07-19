import React, { useContext, useEffect, useState } from 'react';
import { AppBar, Toolbar, Box, IconButton, Typography, CircularProgress } from '@mui/material';
import { Brightness4, Brightness7 } from '@mui/icons-material';
import SearchBar from "./SearchBar";
import DateSelect from "./DateSelect";
import { useThemeContext } from '../contexts/ThemeContext';
import { EventsContext } from '../contexts/EventsContext';
import logo from '../images/logo1.png'; // Make sure to place your logo file in the src/assets/ directory
import '../styles/TopBar.css'; // Import the new CSS file

const TopBar = ({ email }) => {
  const { mode, toggleTheme } = useThemeContext();
  const { businessDate, setBusinessDate, fetchEvents } = useContext(EventsContext);
  const [refreshInterval, setRefreshInterval] = useState(parseInt(process.env.REACT_APP_REFRESH_INTERVAL_SECONDS) || 60);
  const [timer, setTimer] = useState(refreshInterval);

  useEffect(() => {
    const interval = setInterval(() => {
      setTimer(prevTimer => (prevTimer === 0 ? refreshInterval : prevTimer - 1));
      if (timer === 0) {
        fetchEvents(businessDate);
        setTimer(refreshInterval);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [businessDate, fetchEvents, refreshInterval, timer]);

  const handleRefreshClick = () => {
    fetchEvents(businessDate);
    setTimer(refreshInterval);
  };

  return (
    <AppBar position="static" color="default" className="topbar">
      <Toolbar className="toolbar">
        <Box display="flex" alignItems="center" sx={{ marginRight: '140px'}}>
          <img src={logo} alt="4Tellr Logo" className="logo" style={{ height: '50px', marginRight: '2rem' }}/>
          <Typography variant="h6" className="logo-text">
            4TELLR
          </Typography>
        </Box>
        <Box>
          <DateSelect selectedDate={businessDate} setSelectedDate={setBusinessDate} />
        </Box>
        <Box ml="auto" display="flex" alignItems="center">
          <Typography variant="body1" style={{ marginRight: '1rem' }}>
            {email}
          </Typography>
          <IconButton onClick={handleRefreshClick} color="inherit">
            <Box position="relative" display="inline-flex">
              <CircularProgress variant="determinate" value={(timer / refreshInterval) * 100} />
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
                <Typography variant="caption" component="div" color="textSecondary">
                  {`${Math.round(timer)}`}
                </Typography>
              </Box>
            </Box>
          </IconButton>
          <IconButton onClick={toggleTheme} color="inherit">
            {mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
