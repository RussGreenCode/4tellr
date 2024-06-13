// src/App.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { Box, Grid, CssBaseline } from '@mui/material';
import Menu from './components/Menu';
import TopBar from './components/TopBar';
import Overview from './pages/Overview';
import Metrics from './pages/Metrics';
import GroupManagement from './pages/GroupManagement';
import Admin from './pages/Admin';
import { EventsProvider } from './contexts/EventsContext';
import { ThemeContextProvider } from './contexts/ThemeContext';
import './styles/App.css';

function App() {
  const [businessDate, setBusinessDate] = useState('2024-05-24'); // Example date

  return (
    <EventsProvider>
      <ThemeContextProvider>
        <CssBaseline />
        <Router>
          <Box>
            <TopBar businessDate={businessDate} setBusinessDate={setBusinessDate} />
            <Grid container>
              <Grid item xs={2}>
                <Menu />
              </Grid>
              <Grid item xs={10} className="chart-container">
                <Routes>
                  <Route path="/" element={<Overview businessDate={businessDate} />} />
                  <Route path="/metrics" element={<Metrics />} />
                  <Route path="/groups" element={<GroupManagement />} />
                  <Route path="/admin" element={<Admin />} />
                </Routes>
              </Grid>
            </Grid>
          </Box>
        </Router>
      </ThemeContextProvider>
    </EventsProvider>
  );
}

export default App;
