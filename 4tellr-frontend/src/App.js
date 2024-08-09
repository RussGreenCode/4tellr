// src/App.js
import React, { useContext, useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { Box, Grid, CssBaseline } from '@mui/material';
import Menu from './components/Menu';
import Login from './pages/Login';
import TopBar from './components/TopBar';
import Overview from './pages/Overview';
import GroupManagement from './pages/GroupManagement';
import AlertManagement from './pages/AlertManagement';
import UserManagement from './pages/UserManagement';
import UserDetails from './pages/UserDetails';
import ChangePassword from './pages/ChangePassword';
import FavouriteGroups from './pages/FavouriteGroups';
import FavouriteAlerts from './pages/FavouriteAlerts';
import CalendarSummary from './pages/CalendarSummary';
import JobManagement from './pages/JobManagement';
import Admin from './pages/Admin';
import { EventsProvider } from './contexts/EventsContext';
import { ThemeContextProvider } from './contexts/ThemeContext';
import './styles/App.css';
import Dashboard from "./pages/Dashboard";
import ProcessStatistics from "./pages/ProcessStatistics";
import GanttChart from "./pages/GanttChart";
import EventMetadata from "./pages/EventMetadata";
import EventDependencies from "./pages/EventDependencies";

function App() {



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
                <TopBar email={email} />
                <Grid container>
                  <Grid item xs={2}>
                    <Menu setIsAuthenticated={setIsAuthenticated} />
                  </Grid>
                  <Grid item xs={10} className="chart-container">
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/details" element={<Overview />} />
                      <Route path="/groups" element={<GroupManagement />} />
                      <Route path="/admin" element={<Admin />} />
                      <Route path="/changePassword" element={<ChangePassword email={email}/>} />
                      <Route path="/userManagement" element={<UserManagement />} />
                      <Route path="/favouriteGroups" element={<FavouriteGroups />} />
                      <Route path="/favouriteAlerts" element={<FavouriteAlerts />} />
                      <Route path="/userDetails" element={<UserDetails />} />
                      <Route path="/jobManagement" element={<JobManagement />} />
                      <Route path="/processStatistics" element={<ProcessStatistics />} />
                      <Route path="/ganttChart" element={<GanttChart/>} />
                      <Route path="/eventMetadata" element={<EventMetadata/>} />
                      <Route path="/eventDependencies" element={<EventDependencies/>} />
                      <Route path="/alerts" element={<AlertManagement/>} />
                      <Route path="/calendarSummary" element={<CalendarSummary/>} />
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
