// src/utils/TransformEvents.js
import moment from 'moment';

export const transformEventsForChart = (events) => {
  return events.map(event => {
    const eventTime = moment(event.TimeValue).toDate();

    let color;
    if (event.outcomeStatus !== 'N/A') {
      color = event.plotStatus === 'NEW' ? 'blue'
        : event.plotStatus === 'ON_TIME' ? 'darkgreen'
        : event.plotStatus === 'MEETS_SLO' ? 'lightgreen'
        : event.plotStatus === 'MEETS_SLA' ? 'orange'
        : event.plotStatus === 'MET_THRESHOLD' ? 'darkgreen'
        : event.plotStatus === 'BREACHED' ? 'darkred'
        : event.plotStatus === 'NOT_REACHED' ? 'grey'
        : event.plotStatus === 'LATE' ? 'red'
        : 'darkred';
    } else if (event.type === 'EXP') {
      color = event.plotStatus === 'NOT_REACHED' ? 'grey'
        : event.plotStatus === 'BREACHED' ? 'darkred'
        : 'pink';
    }

    return {
      type: event.type,
      time: eventTime.getTime(),
      event: event.eventName,
      status: event.eventStatus,
      sequence: event.eventSequence,
      businessDate: event.businessDate,
      result: event.plotStatus,
      size: 5,
      color,
      yCoordinate: event.eventKey,
      expectationTime: event.type === 'EXP' ? eventTime.getTime() : null // Add expectation time for sorting
    };
  });
};
