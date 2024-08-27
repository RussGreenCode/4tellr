import React, {useContext, useEffect, useState} from 'react';
import { Box, Button, TextField, Typography, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import {EventsContext} from "../contexts/EventsContext";
import axios from "axios";
import config from '../config';

const Login = ({ onLogin, onLogout}) => {
  const {setCurrentUser, fetchUser, resetState} = useContext(EventsContext);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const navigate = useNavigate(); // Get the navigate function from react-router-dom

  useEffect(() => {
    onLogout();
    resetState();
  }, []);

  const handleLogin = async () => {
    try {
      const userDetails = { email: email, password: password };


      const app_prefix=`${config.baseUrl}/api/login`

      const response = await axios.post(app_prefix, userDetails);

      if(response.data.isAuthenticated) {
        setIsAuthenticated(response.data.isAuthenticated);
        onLogin(email);
        setCurrentUser(response.data.user);

        fetchUser(email)

        navigate('/'); // Navigate to the dashboard upon successful login
      } else {
        alert('Please enter both username and password');
      }
    } catch (error) {
      console.error('Error saving group:', error);
    }
  };

  return (
    <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
      <Paper elevation={3} style={{ padding: '2rem', minWidth: '300px' }}>
        <Typography variant="h4" gutterBottom>
          Login
        </Typography>
        <TextField
          label="Email"
          variant="outlined"
          fullWidth
          margin="normal"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <TextField
          label="Password"
          type="password"
          variant="outlined"
          fullWidth
          margin="normal"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <Button variant="contained" color="primary" fullWidth onClick={handleLogin} style={{ marginTop: '1rem' }}>
          Login
        </Button>
      </Paper>
    </Box>
  );
};

export default Login;
