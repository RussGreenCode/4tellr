// src/components/SummaryMetrics.js
import React, { useContext } from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { EventsContext } from '../../contexts/EventsContext';
import '../../styles/SummaryMetrics.css'; // Import the CSS file

const SummaryMetrics = ( {metrics} ) => {


  const COLORS = ['#FF0000', '#FFD700', '#90EE90', '#008000']; // Colors for LATE, MEETS_SLA, MEETS_SLO, ON_TIME

  const data = [
    { name: 'Late', value: metrics.eventStatus.LATE, color: '#FF0000' },
    { name: 'Meets SLA', value: metrics.eventStatus.MEETS_SLA, color: '#FFD700' },
    { name: 'Meets SLO', value: metrics.eventStatus.MEETS_SLO, color: '#90EE90' },
    { name: 'On Time', value: metrics.eventStatus.ON_TIME, color: '#008000' },
    { name: 'On Waiting', value: metrics.eventStatus.NOT_REACHED_EXP, color: '#aaafff' },
  ];


  const renderCustomizedLabel = ({ cx, cy }) => {
    return (
      <text x={cx} y={cy} fill="black" textAnchor="middle" dominantBaseline="central">
        {`${metrics.summary.percentageComplete.toFixed(0)}%`}
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
            <Typography variant="h6">Running Late</Typography>
            <Typography variant="h4">{metrics.eventStatus.BREACHED_EXP}</Typography>
          </Paper>
        </Grid>
        <Grid item>
          <Paper className="status-block waiting">
            <Typography variant="h6">Waiting</Typography>
            <Typography variant="h4">{metrics.eventStatus.NOT_REACHED_EXP}</Typography>
          </Paper>
        </Grid>
        <Grid item>
          <Paper className="status-block late">
            <Typography variant="h6">Arrived Late</Typography>
            <Typography variant="h4">{metrics.eventStatus.LATE}</Typography>
          </Paper>
        </Grid>
        <Grid item>
          <Paper className="status-block meets-sla">
            <Typography variant="h6">Met SLA</Typography>
            <Typography variant="h4">{metrics.eventStatus.MEETS_SLA}</Typography>
          </Paper>
        </Grid>
        <Grid item>
          <Paper className="status-block meets-slo">
            <Typography variant="h6">Met SLO</Typography>
            <Typography variant="h4">{metrics.eventStatus.MEETS_SLO}</Typography>
          </Paper>
        </Grid>
        <Grid item>
          <Paper className="status-block on-time">
            <Typography variant="h6">Met EXP</Typography>
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
