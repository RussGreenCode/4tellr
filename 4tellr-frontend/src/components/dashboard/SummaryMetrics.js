// src/components/SummaryMetrics.js
import React, { useMemo } from 'react';
import { Grid, Box, Paper} from '@mui/material';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import CurrentStatusBlock from './CurrentStatusBlock';
import { generateBarData } from '../../utils/MetricsHelper';
import '../../styles/SummaryMetrics.css'; // Import the CSS file

const SummaryMetrics = ({ metrics }) => {
  const COLORS = ['#FF0000', '#FFD700', '#90EE90', '#008000']; // Colors for LATE, MEETS_SLA, MEETS_SLO, ON_TIME

  const data = useMemo(() => generateBarData(metrics), [metrics]);


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
          <CurrentStatusBlock
            label="Error"
            value={metrics.eventStatus.ERROR}
            plotStatus="ERROR"
            className="error"
          />
        </Grid>
        <Grid item>
          <CurrentStatusBlock
            label="Running Late"
            value={metrics.eventStatus.BREACHED_EXP}
            plotStatus="BREACHED"
            className="not-met-exp"
          />
        </Grid>
        <Grid item>
          <CurrentStatusBlock
            label="Waiting"
            value={metrics.eventStatus.NOT_REACHED_EXP}
            plotStatus="NOT_REACHED_EXP"
            className="waiting"
          />
        </Grid>
        <Grid item>
          <CurrentStatusBlock
            label="Arrived Late"
            value={metrics.eventStatus.LATE}
            plotStatus="LATE"
            className="late"
          />
        </Grid>
        <Grid item>
          <CurrentStatusBlock
            label="Met SLA"
            value={metrics.eventStatus.MEETS_SLA}
            plotStatus="MEETS_SLA"
            className="meets-sla"
          />
        </Grid>
        <Grid item>
          <CurrentStatusBlock
            label="Met SLO"
            value={metrics.eventStatus.MEETS_SLO}
            plotStatus="MEETS_SLO"
            className="meets-slo"
          />
        </Grid>
        <Grid item>
          <CurrentStatusBlock
            label="Met EXP"
            value={metrics.eventStatus.ON_TIME}
            plotStatus="ON_TIME"
            className="on-time"
          />
        </Grid>
        <Grid item>
          <CurrentStatusBlock
            label="New Event"
            value={metrics.eventStatus.NEW}
            plotStatus="NEW_EVT"
            className="new-event"
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default SummaryMetrics;
