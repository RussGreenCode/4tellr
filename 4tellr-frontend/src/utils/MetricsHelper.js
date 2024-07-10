// src/utils/MetricsHelper.js
export const generateBarData = (filteredMetrics) => {
  return [
    { name: 'Error', value: filteredMetrics.eventStatus.ERROR, color: 'darkred', eventType: 'ERROR' },
    { name: 'Running Late', value: filteredMetrics.eventStatus.BREACHED_EXP, color: 'darkred', eventType: 'BREACHED' },
    { name: 'Waiting', value: filteredMetrics.eventStatus.NOT_REACHED_EXP, color: 'grey', eventType: 'NOT_REACHED_EXP' },
    { name: 'Missed SLA', value: filteredMetrics.eventStatus.LATE, color: 'red', eventType: 'LATE' },
    { name: 'Missed SLO', value: filteredMetrics.eventStatus.MEETS_SLA, color: 'orange', eventType: 'MEETS_SLA' },
    { name: 'Missed EXP', value: filteredMetrics.eventStatus.MEETS_SLO, color: 'darkgreen', eventType: 'MEETS_SLO' },
    { name: 'On Time', value: filteredMetrics.eventStatus.ON_TIME, color: 'lightgreen', eventType: 'ON_TIME' },
    { name: 'New', value: filteredMetrics.eventStatus.NEW, color: 'blue', eventType: 'NEW' },
  ];
};
