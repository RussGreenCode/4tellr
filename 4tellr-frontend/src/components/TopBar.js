// src/components/TopBar.js
import React, { useContext } from 'react';
import { AppBar, Toolbar, Box, IconButton, Typography } from '@mui/material';
import { Brightness4, Brightness7 } from '@mui/icons-material';
import SearchBar from "./SearchBar";
import DateSelect from "./DateSelect";
import { useThemeContext } from '../contexts/ThemeContext';
import { EventsContext } from '../contexts/EventsContext';
import '../styles/App.css'; // Import the new CSS file

const TopBar = ({ email }) => {
  const { mode, toggleTheme } = useThemeContext();
  const { businessDate, setBusinessDate, setSearchCriteria } = useContext(EventsContext);

  return (
    <AppBar position="static" color="default" className="topbar">
      <Toolbar>
        <DateSelect selectedDate={businessDate} setSelectedDate={setBusinessDate} />
        <SearchBar setSearchEntry={setSearchCriteria} />
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
