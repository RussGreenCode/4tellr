// src/App.js
import React, { useContext, useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { Box, Grid, CssBaseline } from '@mui/material';
import Menu from './components/Menu';
import Login from './pages/Login';
import TopBar from './components/TopBar';
import Overview from './pages/Overview';
import Metrics from './pages/Metrics';
import GroupManagement from './pages/GroupManagement';
import UserManagement from './pages/UserManagement';
import ChangePassword from './pages/ChangePassword';
import FavouriteGroups from './pages/FavouriteGroups';
import Admin from './pages/Admin';
import { EventsProvider } from './contexts/EventsContext';
import { ThemeContextProvider } from './contexts/ThemeContext';
import './styles/App.css';

function App() {
  const [businessDate, setBusinessDate] = useState('2024-05-24'); // Example date
  const [email, setEmail] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = (email) => {
    setIsAuthenticated(true);
    setEmail(email);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setEmail('');
  };

  return (
    <EventsProvider email={email}>
      <ThemeContextProvider>
        <CssBaseline />
        <Router>
          <Box>
            {isAuthenticated ? (
              <>
                <TopBar businessDate={businessDate} setBusinessDate={setBusinessDate} email={email} />
                <Grid container>
                  <Grid item xs={2}>
                    <Menu setIsAuthenticated={setIsAuthenticated} />
                  </Grid>
                  <Grid item xs={10} className="chart-container">
                    <Routes>
                      <Route path="/" element={<Overview />} />
                      <Route path="/metrics" element={<Metrics />} />
                      <Route path="/groups" element={<GroupManagement />} />
                      <Route path="/admin" element={<Admin />} />
                      <Route path="/changePassword" element={<ChangePassword email={email}/>} />
                      <Route path="/userManagement" element={<UserManagement />} />
                      <Route path="/favouriteGroups" element={<FavouriteGroups />} />
                    </Routes>
                  </Grid>
                </Grid>
              </>
            ) : (
              <Login onLogin={handleLogin} />
            )}
          </Box>
        </Router>
      </ThemeContextProvider>
    </EventsProvider>
  );
}

export default App;
