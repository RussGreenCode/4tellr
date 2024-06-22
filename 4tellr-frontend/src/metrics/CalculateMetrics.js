// src/metrics/CalculateMetrics.js
const CalculateMetrics = (events) => {
  let totalEvents = events.length;

  let categorizedEvents = {
    ON_TIME: [],
    MEETS_SLO: [],
    MEETS_SLA: [],
    LATE: [],
    ERROR: [],
    NEW_EVENT: [],
    NOT_MET_EXP: [],
    EXP: [],
  };

  events.forEach(event => {
    if (categorizedEvents[event.outcomeStatus]) {
      categorizedEvents[event.outcomeStatus].push(event);
    }

    if (event.type === 'EXP') {
      categorizedEvents.EXP.push(event);
    }

    if (event.outcomeStatus === 'NOT_MET_EXP') {
      categorizedEvents.NOT_MET_EXP.push(event);
    }

    if (event.outcomeStatus === 'NEW_EVENT') {
      categorizedEvents.NEW_EVENT.push(event);
    }
  });

  let expectationCount = totalEvents + categorizedEvents.NOT_MET_EXP.length;

  return {
    summary: {
      totalEvents,
      expectationCount,
      percentageComplete: expectationCount !== 0 ? (totalEvents / expectationCount) * 100 : 0,
    },
    eventStatus: {
      ON_TIME: categorizedEvents.ON_TIME.length,
      MEETS_SLO: categorizedEvents.MEETS_SLO.length,
      MEETS_SLA: categorizedEvents.MEETS_SLA.length,
      LATE: categorizedEvents.LATE.length,
      ERROR: categorizedEvents.ERROR.length,
      NEW_EVENT: categorizedEvents.NEW_EVENT.length,
      NOT_MET_EXP: categorizedEvents.NOT_MET_EXP.length,
    }
  };
};

export default CalculateMetrics;
