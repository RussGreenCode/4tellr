// src/pages/JobManagement.js
import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, List, ListItem, ListItemText, IconButton, TextField, Select, MenuItem, Grid} from '@mui/material';
import { Add, Delete, Edit, Pause, PlayArrow as Resume, FlashOn, Save } from '@mui/icons-material';
import axios from 'axios';
import config from '../config';

const JobManagement = () => {
  const [jobs, setJobs] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [newJob, setNewJob] = useState({
    id: '',
    name: '',
    trigger: 'interval',
    intervalType: 'seconds',
    intervalValue: 60,
    url: '',
    params: {businessDate: new Date().toISOString().split('T')[0]}
  });
  const [overrideParams, setOverrideParams] = useState('');

  useEffect(() => {
    fetchJobs();
  }, []);


  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${config.baseUrl}/api/jobs`);
      if (response.data.success) {
        setJobs(response.data.data);
      } else {
        console.error('Error fetching jobs:', response.data.error);
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const handleCreateOrUpdateJob = async () => {
    const intervalSeconds = convertIntervalToSeconds(newJob.intervalType, newJob.intervalValue);
    const jobToSave = {
      ...newJob,
      seconds: intervalSeconds
    };

    try {
      const response = isEditing
        ? await axios.put(`${config.baseUrl}/api/jobs/${newJob.id}`, jobToSave)
        : await axios.post(`${config.baseUrl}/api/jobs`, jobToSave);

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
        setIsEditing(false);
      } else {
        console.error(`Error ${isEditing ? 'updating' : 'creating'} job:`, response.data.error);
      }
    } catch (error) {
      console.error(`Error ${isEditing ? 'updating' : 'creating'} job:`, error);
    }
  };


  const handleDeleteJob = async (jobId) => {
    try {
      const response = await axios.delete(`${config.baseUrl}/api/jobs/${jobId}`);
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
      const response = await axios.post(`${config.baseUrl}/api/jobs/trigger/${jobId}`, {params});
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
      const response = await axios.post(`${config.baseUrl}/api/jobs/pause/${jobId}`);
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
      const response = await axios.post(`${config.baseUrl}/api/jobs/resume/${jobId}`);
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

  const handleEditJob = (job) => {
    const intervalValue = job.trigger.interval.seconds;
    setNewJob({
      id: job.id,
      name: job.name,
      trigger: job.trigger,
      intervalType: 'seconds',
      intervalValue,
      url: job.args[0],
      params: job.kwargs.params
    });
    setIsEditing(true);
  };


  return (
      <Box p={3}>
        <Typography variant="h4" gutterBottom>Job Management</Typography>
        <Box mb={3}>
          <Typography variant="h6">{isEditing ? 'Edit Job' : 'Create New Job'}</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                  label="Job ID"
                  value={newJob.id}
                  onChange={(e) => setNewJob({...newJob, id: e.target.value})}
                  fullWidth
                  margin="normal"
                  disabled={isEditing}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                  label="Job Name"
                  value={newJob.name}
                  onChange={(e) => setNewJob({...newJob, name: e.target.value})}
                  fullWidth
                  margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <Select
                  label="Trigger Type"
                  value={newJob.trigger}
                  onChange={(e) => setNewJob({...newJob, trigger: e.target.value})}
                  fullWidth
                  margin="normal"
              >
                <MenuItem value="interval">Interval</MenuItem>
                <MenuItem value="cron">Cron</MenuItem>
              </Select>
            </Grid>
            {newJob.trigger === 'interval' && (
                <>
                  <Grid item xs={12}>
                    <Select
                        label="Interval Type"
                        value={newJob.intervalType}
                        onChange={(e) => setNewJob({...newJob, intervalType: e.target.value})}
                        fullWidth
                        margin="normal"
                    >
                      <MenuItem value="hours">Hours</MenuItem>
                      <MenuItem value="minutes">Minutes</MenuItem>
                      <MenuItem value="seconds">Seconds</MenuItem>
                    </Select>
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                        label="Interval Value"
                        type="number"
                        value={newJob.intervalValue}
                        onChange={(e) => setNewJob({...newJob, intervalValue: parseInt(e.target.value, 10)})}
                        fullWidth
                        margin="normal"
                    />
                  </Grid>
                </>
            )}
            <Grid item xs={12}>
              <TextField
                  label="URL"
                  value={newJob.url}
                  onChange={(e) => setNewJob({...newJob, url: e.target.value})}
                  fullWidth
                  margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                  label="Params (JSON)"
                  value={JSON.stringify(newJob.params)}
                  onChange={(e) => setNewJob({...newJob, params: JSON.parse(e.target.value)})}
                  fullWidth
                  margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                  variant="contained"
                  color="primary"
                  startIcon={isEditing ? <Save/> : <Add/>}
                  onClick={handleCreateOrUpdateJob}
              >
                {isEditing ? 'Save Job' : 'Create Job'}
              </Button>
            </Grid>
          </Grid>
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
                <Box display="flex" alignItems="center">
                  <TextField
                    label="Override Params (JSON)"
                    value={overrideParams}
                    onChange={(e) => setOverrideParams(e.target.value)}
                    margin="normal"
                    size="small"
                    style={{ marginRight: '10px' }}
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
                  <IconButton edge="end" aria-label="edit" onClick={() => handleEditJob(job.id)}>
                    <Edit />
                  </IconButton>
                  <IconButton edge="end" aria-label="delete" onClick={() => handleDeleteJob(job.id)}>
                    <Delete />
                  </IconButton>
                </Box>
              </ListItem>
            ))}
          </List>
        </Box>
      </Box>
  );
};
export default JobManagement;
