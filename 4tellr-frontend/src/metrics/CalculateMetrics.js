// src/metrics/CalculateMetrics.js
const CalculateMetrics = (events) => {
  let totalEvents = events.length;

  let categorizedEvents = {
    ON_TIME: [],
    MEETS_SLO: [],
    MEETS_SLA: [],
    LATE: [],
    ERROR: [],
    NEW_EVT: [],
    NO_ASSO_EVT: [],
    EXP: [],
  };

  events.forEach(event => {
    if (categorizedEvents[event.outcomeStatus]) {
      categorizedEvents[event.outcomeStatus].push(event);
    }

    if (event.type === 'EXP') {
      categorizedEvents.EXP.push(event);
    }

  });

  let expectationCount = totalEvents + categorizedEvents.NO_ASSO_EVT.length;

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
      NEW_EVT: categorizedEvents.NEW_EVT.length,
      NO_ASSO_EVT: categorizedEvents.NO_ASSO_EVT.length,
    }
  };
};

export default CalculateMetrics;
