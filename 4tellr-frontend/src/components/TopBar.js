// src/components/TopBar.js
import React, { useContext } from 'react';
import { AppBar, Toolbar, Box, IconButton, Typography } from '@mui/material';
import { Brightness4, Brightness7 } from '@mui/icons-material';
import SearchBar from "./SearchBar";
import DateSelect from "./DateSelect";
import { useThemeContext } from '../contexts/ThemeContext';
import { EventsContext } from '../contexts/EventsContext';
import logo from '../images/logo1.png'; // Make sure to place your logo file in the src/assets/ directory
import '../styles/TopBar.css'; // Import the new CSS file

const TopBar = ({ email }) => {
  const { mode, toggleTheme } = useThemeContext();
  const { businessDate, setBusinessDate } = useContext(EventsContext);

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
          <IconButton onClick={toggleTheme} color="inherit">
            {mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
