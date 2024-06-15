import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from "axios";

const Login = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const navigate = useNavigate(); // Get the navigate function from react-router-dom

  const handleLogin = async () => {
    try {
      const userDetails = { email: email, password: password };
      const response = await axios.post('http://127.0.0.1:5000/api/login', userDetails);

      if(response.data.isAuthenticated) {
        setIsAuthenticated(response.data.isAuthenticated);
        onLogin(email);
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
