// src/pages/JobManagement.js
import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, List, ListItem, ListItemText, ListItemSecondaryAction, IconButton, TextField, Select, MenuItem } from '@mui/material';
import { Add, Delete, Pause, PlayArrow as Resume, FlashOn } from '@mui/icons-material';
import axios from 'axios';

const JobManagement = () => {
  const [jobs, setJobs] = useState([]);
  const [newJob, setNewJob] = useState({
    id: '',
    name: '',
    trigger: 'interval',
    intervalType: 'seconds',
    intervalValue: 60,
    url: '',
    params: { businessDate: new Date().toISOString().split('T')[0] }
  });
  const [overrideParams, setOverrideParams] = useState('');

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/jobs');
      if (response.data.success) {
        setJobs(response.data.data);
      } else {
        console.error('Error fetching jobs:', response.data.error);
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const handleCreateJob = async () => {
    const intervalSeconds = convertIntervalToSeconds(newJob.intervalType, newJob.intervalValue);
    const jobToCreate = {
      ...newJob,
      seconds: intervalSeconds
    };

    try {
      const response = await axios.post('http://127.0.0.1:5000/api/jobs', jobToCreate);
      if (response.data.success) {
        fetchJobs();
        setNewJob({
          id: '',
          name: '',
          trigger: 'interval',
          intervalType: 'seconds',
          intervalValue: 60,
          url: '',
          params: { businessDate: new Date().toISOString().split('T')[0] }
        });
      } else {
        console.error('Error creating job:', response.data.error);
      }
    } catch (error) {
      console.error('Error creating job:', error);
    }
  };

  const handleDeleteJob = async (jobId) => {
    try {
      const response = await axios.delete(`http://127.0.0.1:5000/api/jobs/${jobId}`);
      if (response.data.success) {
        fetchJobs();
      } else {
        console.error('Error deleting job:', response.data.error);
      }
    } catch (error) {
      console.error('Error deleting job:', error);
    }
  };

  const handleTriggerJob = async (jobId) => {
    try {
      const params = overrideParams ? JSON.parse(overrideParams) : undefined;
      const response = await axios.post(`http://127.0.0.1:5000/api/jobs/trigger/${jobId}`, { params });
      if (response.data.success) {
        console.log('Job triggered successfully');
      } else {
        console.error('Error triggering job:', response.data.error);
      }
    } catch (error) {
      console.error('Error triggering job:', error);
    }
  };

  const handlePauseJob = async (jobId) => {
    try {
      const response = await axios.post(`http://127.0.0.1:5000/api/jobs/pause/${jobId}`);
      if (response.data.success) {
        fetchJobs();
      } else {
        console.error('Error pausing job:', response.data.error);
      }
    } catch (error) {
      console.error('Error pausing job:', error);
    }
  };

  const handleResumeJob = async (jobId) => {
    try {
      const response = await axios.post(`http://127.0.0.1:5000/api/jobs/resume/${jobId}`);
      if (response.data.success) {
        fetchJobs();
      } else {
        console.error('Error resuming job:', response.data.error);
      }
    } catch (error) {
      console.error('Error resuming job:', error);
    }
  };

  const convertIntervalToSeconds = (type, value) => {
    switch (type) {
      case 'hours':
        return value * 3600;
      case 'minutes':
        return value * 60;
      case 'seconds':
      default:
        return value;
    }
  };

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>Job Management</Typography>
      <Box mb={3}>
        <Typography variant="h6">Create New Job</Typography>
        <TextField
          label="Job ID"
          value={newJob.id}
          onChange={(e) => setNewJob({ ...newJob, id: e.target.value })}
          fullWidth
          margin="normal"
        />
        <TextField
          label="Job Name"
          value={newJob.name}
          onChange={(e) => setNewJob({ ...newJob, name: e.target.value })}
          fullWidth
          margin="normal"
        />
        <Select
          label="Trigger Type"
          value={newJob.trigger}
          onChange={(e) => setNewJob({ ...newJob, trigger: e.target.value })}
          fullWidth
          margin="normal"
        >
          <MenuItem value="interval">Interval</MenuItem>
          <MenuItem value="cron">Cron</MenuItem>
        </Select>
        {newJob.trigger === 'interval' && (
          <>
            <Select
              label="Interval Type"
              value={newJob.intervalType}
              onChange={(e) => setNewJob({ ...newJob, intervalType: e.target.value })}
              fullWidth
              margin="normal"
            >
              <MenuItem value="hours">Hours</MenuItem>
              <MenuItem value="minutes">Minutes</MenuItem>
              <MenuItem value="seconds">Seconds</MenuItem>
            </Select>
            <TextField
              label="Interval Value"
              type="number"
              value={newJob.intervalValue}
              onChange={(e) => setNewJob({ ...newJob, intervalValue: parseInt(e.target.value, 10) })}
              fullWidth
              margin="normal"
            />
          </>
        )}
        <TextField
          label="URL"
          value={newJob.url}
          onChange={(e) => setNewJob({ ...newJob, url: e.target.value })}
          fullWidth
          margin="normal"
        />
        <TextField
          label="Params (JSON)"
          value={JSON.stringify(newJob.params)}
          onChange={(e) => setNewJob({ ...newJob, params: JSON.parse(e.target.value) })}
          fullWidth
          margin="normal"
        />
        <Button variant="contained" color="primary" startIcon={<Add />} onClick={handleCreateJob}>
          Create Job
        </Button>
      </Box>
      <Box>
        <Typography variant="h6">Existing Jobs</Typography>
        <List>
          {jobs.map((job) => (
            <ListItem key={job.id}>
              <ListItemText
                primary={`${job.name} (${job.id})`}
                secondary={`Next run: ${job.next_run_time} | Trigger: ${job.trigger} | args: ${job.args}`}
              />
              <ListItemSecondaryAction>
                <TextField
                  label="Override Params (JSON)"
                  value={overrideParams}
                  onChange={(e) => setOverrideParams(e.target.value)}
                  fullWidth
                  margin="normal"
                />
                <IconButton edge="end" aria-label="trigger" onClick={() => handleTriggerJob(job.id)}>
                  <FlashOn />
                </IconButton>
                <IconButton edge="end" aria-label="pause" onClick={() => handlePauseJob(job.id)}>
                  <Pause />
                </IconButton>
                <IconButton edge="end" aria-label="resume" onClick={() => handleResumeJob(job.id)}>
                  <Resume />
                </IconButton>
                <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteJob(job.id)}>
                  <Delete />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Box>
    </Box>
  );
};

export default JobManagement;
