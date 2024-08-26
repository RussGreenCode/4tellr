import React, { useState, useEffect } from 'react';
import { Typography, Paper, Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { styled } from '@mui/system';
import axios from 'axios';

// Define styled components
const StyledTableCellHeader = styled(TableCell)(({ theme }) => ({
  padding: '4px 8px',
  fontSize: '0.875rem',
}));

const StyledTableCell = styled(TableCell)(({ theme }) => ({
  padding: '8px 8px',
}));

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  display: 'flex',
  alignItems: 'center',
}));

const StyledGridContainer = styled(Grid)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
}));

const StyledTypographyLeft = styled('div')(({ theme }) => ({
  textAlign: 'left',
  lineHeight: 1.6,
  marginBottom: theme.spacing(1),
}));

const EventDetailsComponent = ({ event, children }) => {
  const [loading, setLoading] = useState(false);
  const [eventData, setEventData] = useState([]);

  useEffect(() => {
    if (event) {
      fetchEventData();
    }
  }, [event]);

  const fetchEventData = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/event', {
        params: {
          event_name: event.event,        // Assuming event.event is the event name
          event_status: event.status,     // Assuming event.status is the event status
          business_date: event.businessDate // Assuming event.businessDate is the business date
        }
      });
      setEventData(response.data);
    } catch (error) {
      console.error('Error fetching event data:', error);
      setEventData([]);
    } finally {
      setLoading(false);
    }
  };

  const formatTPlusTime = (baseTime, additionalTime) => {
    const totalSeconds = baseTime.seconds + additionalTime.seconds;
    const extraMinutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;

    const totalMinutes = baseTime.minutes + additionalTime.minutes + extraMinutes;
    const extraHours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;

    const totalHours = baseTime.hours + additionalTime.hours + extraHours;
    const extraDays = Math.floor(totalHours / 24);
    const hours = totalHours % 24;

    const days = baseTime.days + additionalTime.days + extraDays;

    return `T+${days} ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  const parseTimeOffset = (baseDate, eventTime) => {
    const base = new Date(baseDate);
    const event = new Date(eventTime);

    const deltaSeconds = (event - base) / 1000;
    const deltaDays = Math.floor(deltaSeconds / 86400);
    const hours = Math.floor((deltaSeconds % 86400) / 3600);
    const minutes = Math.floor(((deltaSeconds % 86400) % 3600) / 60);
    const seconds = Math.floor(((deltaSeconds % 86400) % 3600) % 60);

    return { days: deltaDays, hours, minutes, seconds };
  };

  const calculateDelta = (actualTime, targetTime) => {
    const delta = (new Date(actualTime) - new Date(targetTime)) / 60000; // Convert milliseconds to minutes
    return `${delta.toFixed(2)} mins`;
  };

  const getBackgroundColor = (status) => {
    switch (status) {
      case 'ON_TIME':
        return '#c8e6c9'; // Green for on time
      case 'MEETS_SLO':
        return '#fff9c4'; // Yellow for meets SLO
      case 'LATE':
      case 'MISSES_SLA':
        return '#ffcdd2'; // Red for late or misses SLA
      default:
        return '#e0e0e0'; // Gray for unknown or neutral status
    }
  };

  const renderCommonInfo = () => (
    <StyledTypographyLeft>
      <Typography><strong>Business Date:</strong> {event.businessDate}</Typography>
      <Typography><strong>Event Name:</strong> {event.event}</Typography>
      <Typography><strong>Event Status:</strong> {event.status}</Typography>
      <Typography><strong>Sequence:</strong> {event.sequence}</Typography>
      <Typography><strong>Event Type:</strong> {event.type}</Typography>
      <Typography><strong>Result:</strong> {event.result}</Typography>
    </StyledTypographyLeft>
  );

  const renderTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <StyledTableCellHeader></StyledTableCellHeader>
            {eventData.map((data, index) => (
              <StyledTableCellHeader key={index} colSpan={2} align="center">
                Sequence {data.sequence} {data.sequence === event.sequence && "(Selected)"}
              </StyledTableCellHeader>
            ))}
          </TableRow>
          <TableRow>
            <StyledTableCellHeader></StyledTableCellHeader>
            {eventData.map((_, index) => (
              <>
                <StyledTableCellHeader key={`predicted-${index}`} align="center"><strong>Predicted</strong></StyledTableCellHeader>
                <StyledTableCellHeader key={`actual-${index}`} align="center"><strong>Actual</strong></StyledTableCellHeader>
              </>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {['Event', 'Exp Delta', 'SLO Delta', 'SLA Delta'].map((row, rowIndex) => (
            <TableRow key={row}>
              <StyledTableCell><strong>{row}</strong></StyledTableCell>
              {eventData.map((data, index) => {
                let predictedTime;
                let actualTime;
                let deltaTime;
                let formattedPredicted;
                let formattedActual;

                switch (row) {
                  case 'Event':
                    predictedTime = parseTimeOffset(event.businessDate, data.expectedTime);
                    actualTime = parseTimeOffset(event.businessDate, data.eventTime);
                    formattedPredicted = formatTPlusTime(predictedTime, { days: 0, hours: 0, minutes: 0, seconds: 0 });
                    formattedActual = formatTPlusTime(actualTime, { days: 0, hours: 0, minutes: 0, seconds: 0 });
                    break;
                  case 'Exp Delta':
                    deltaTime = calculateDelta(data.eventTime, data.expectedTime);
                    formattedPredicted = formatTPlusTime(parseTimeOffset(event.businessDate, data.expectedTime), { days: 0, hours: 0, minutes: 0, seconds: 0 });
                    break;
                  case 'SLO Delta':
                    deltaTime = calculateDelta(data.eventTime, data.sloTime);
                    formattedPredicted = formatTPlusTime(parseTimeOffset(event.businessDate, data.sloTime), { days: 0, hours: 0, minutes: 0, seconds: 0 });
                    break;
                  case 'SLA Delta':
                    deltaTime = calculateDelta(data.eventTime, data.slaTime);
                    formattedPredicted = formatTPlusTime(parseTimeOffset(event.businessDate, data.slaTime), { days: 0, hours: 0, minutes: 0, seconds: 0 });
                    break;
                  default:
                    break;
                }

                const bgColor = getBackgroundColor(data.outcomeStatus);

                return (
                  <>
                    <StyledTableCell key={`predicted-${index}-${row}`} align="center" style={{ backgroundColor: bgColor }}>
                      {row === 'Event' ? formattedPredicted : formattedPredicted}
                    </StyledTableCell>
                    <StyledTableCell key={`actual-${index}-${row}`} align="center" style={{ backgroundColor: bgColor }}>
                      {row === 'Event' ? formattedActual : deltaTime}
                    </StyledTableCell>
                  </>
                );
              })}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <StyledPaper elevation={1}>
      {loading ? (
        <Typography>Loading...</Typography>
      ) : eventData.length > 0 ? (
        <StyledGridContainer container spacing={2}>
          <Grid item xs={12} sm={4}>
            {renderCommonInfo()}
          </Grid>
          <Grid item xs={12} sm={8}>
            {renderTable()}
          </Grid>
        </StyledGridContainer>
      ) : (
        <Typography>No event selected or data not found</Typography>
      )}
      {children}
    </StyledPaper>
  );
};

export default EventDetailsComponent;
