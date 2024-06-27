// src/components/SummaryMetrics.js
import React, { useContext } from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { EventsContext } from '../../contexts/EventsContext';
import '../../styles/SummaryMetrics.css'; // Import the CSS file

const SummaryMetrics = () => {
  const { metrics } = useContext(EventsContext);

  const COLORS = ['#FF0000', '#FFD700', '#90EE90', '#008000']; // Colors for LATE, MEETS_SLA, MEETS_SLO, ON_TIME

  const data = [
    { name: 'Late', value: metrics.eventStatus.LATE, color: '#FF0000' },
    { name: 'Meets SLA', value: metrics.eventStatus.MEETS_SLA, color: '#FFD700' },
    { name: 'Meets SLO', value: metrics.eventStatus.MEETS_SLO, color: '#90EE90' },
    { name: 'On Time', value: metrics.eventStatus.ON_TIME, color: '#008000' },
  ];

  const totalStatus = data.reduce((acc, item) => acc + item.value, 0);
  const remaining = metrics.summary.expectationCount - totalStatus;
  if (remaining > 0) {
    data.push({ name: 'Remaining', value: remaining, color: '#E0E0E0' }); // Adjust color for light/dark mode
  }

  const renderCustomizedLabel = ({ cx, cy }) => {
    return (
      <text x={cx} y={cy} fill="black" textAnchor="middle" dominantBaseline="central">
        {`${metrics.summary.percentageComplete.toFixed(2)}%`}
      </text>
    );
  };

  return (
    <Box sx={{ overflowX: 'auto' }}>
      <Grid container spacing={3} sx={{ flexWrap: 'nowrap', width: 'max-content' }}>
        <Grid item>
          <Paper className="status-block">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  innerRadius="70%"
                  outerRadius="95%"
                  dataKey="value"
                  labelLine={false}
                  label={renderCustomizedLabel}
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item>
          <Paper className="status-block error">
            <Typography variant="h6">Error</Typography>
            <Typography variant="h4">{metrics.eventStatus.ERROR}</Typography>
          </Paper>
        </Grid>
        <Grid item>
          <Paper className="status-block not-met-exp">
            <Typography variant="h6">No Event Yet</Typography>
            <Typography variant="h4">{metrics.eventStatus.NO_ASSO_EVT}</Typography>
          </Paper>
        </Grid>
        <Grid item>
          <Paper className="status-block late">
            <Typography variant="h6">Late</Typography>
            <Typography variant="h4">{metrics.eventStatus.LATE}</Typography>
          </Paper>
        </Grid>
        <Grid item>
          <Paper className="status-block meets-sla">
            <Typography variant="h6">Meets SLA</Typography>
            <Typography variant="h4">{metrics.eventStatus.MEETS_SLA}</Typography>
          </Paper>
        </Grid>
        <Grid item>
          <Paper className="status-block meets-slo">
            <Typography variant="h6">Meets SLO</Typography>
            <Typography variant="h4">{metrics.eventStatus.MEETS_SLO}</Typography>
          </Paper>
        </Grid>
        <Grid item>
          <Paper className="status-block on-time">
            <Typography variant="h6">On Time</Typography>
            <Typography variant="h4">{metrics.eventStatus.ON_TIME}</Typography>
          </Paper>
        </Grid>
        <Grid item>
          <Paper className="status-block new-event">
            <Typography variant="h6">New Event</Typography>
            <Typography variant="h4">{metrics.eventStatus.NEW_EVT}</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SummaryMetrics;
