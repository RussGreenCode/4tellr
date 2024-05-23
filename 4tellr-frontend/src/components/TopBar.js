// src/components/TopBar.js
import React, { useState } from 'react';
import { AppBar, Toolbar, Box, Button, Popover, TextField, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/App.css';
import SearchBar from "./SearchBar";
import DateSelect from "./DateSelect";

const TopBar = () => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

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
      <Toolbar>
        <DateSelect />
        <SearchBar />
        <Box ml="auto">
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
