// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { Box, Grid } from '@mui/material';
import Menu from './components/Menu';
import TopBar from './components/TopBar';
import SearchBar from './components/SearchBar';
import Overview from './pages/Overview';
import Metrics from './pages/Metrics';
import Settings from './pages/Settings';
import './styles/App.css';

function App() {
  return (
    <Router>
      <Box>
        <TopBar />
        <Grid container>
          <Grid item xs={2}>
            <Menu />
          </Grid>
          <Grid item xs={10} className="chart-container">
            <Routes>
              <Route path="/" element={<Overview />} />
              <Route path="/metrics" element={<Metrics />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Grid>
        </Grid>
      </Box>
    </Router>
  );
}

export default App;
