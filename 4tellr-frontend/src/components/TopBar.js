// src/components/TopBar.js
import React, { useState, useContext } from 'react';
import { AppBar, Toolbar, Box, Button, Popover, TextField, Typography, IconButton } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Brightness4, Brightness7 } from '@mui/icons-material';
import axios from 'axios';
import SearchBar from "./SearchBar";
import DateSelect from "./DateSelect";
import { useThemeContext } from '../contexts/ThemeContext';
import { EventsContext } from '../contexts/EventsContext';
import '../styles/App.css';

const TopBar = () => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { mode, toggleTheme } = useThemeContext();
  const { businessDate, setBusinessDate } = useContext(EventsContext);

  const handleLoginClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleEmailChange = (event) => {
    setEmail(event.target.value);
  };

  const handlePasswordChange = (event) => {
    setPassword(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post('/login', { email, password });
      if (response.data.success) {
        // handle successful login
        navigate('/');
      } else {
        setError(response.data.message);
      }
    } catch (error) {
      setError('Login failed. Please try again.');
    }
  };

  const open = Boolean(anchorEl);
  const id = open ? 'simple-popover' : undefined;

  return (
    <AppBar position="static" color="default">
      <Toolbar style={{ display: 'flex', alignItems: 'center' }}>
        <DateSelect selectedDate={businessDate} setSelectedDate={setBusinessDate} />
        <SearchBar />
        <Box ml="auto" display="flex" alignItems="center">
          <IconButton onClick={toggleTheme} color="inherit">
            {mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>
          <Button variant="contained" color="primary" onClick={handleLoginClick}>
            Login
          </Button>
          <Popover
            id={id}
            open={open}
            anchorEl={anchorEl}
            onClose={handleClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'left',
            }}
          >
            <Box p={2}>
              <Typography variant="h6">Login</Typography>
              {error && <Typography color="error">{error}</Typography>}
              <form onSubmit={handleSubmit}>
                <TextField
                  label="Email"
                  type="email"
                  fullWidth
                  margin="normal"
                  value={email}
                  onChange={handleEmailChange}
                />
                <TextField
                  label="Password"
                  type="password"
                  fullWidth
                  margin="normal"
                  value={password}
                  onChange={handlePasswordChange}
                />
                <Button type="submit" variant="contained" color="primary" fullWidth>
                  Submit
                </Button>
              </form>
            </Box>
          </Popover>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
