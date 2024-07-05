// src/metrics/CalculateMetrics.js
const CalculateMetrics = (events) => {
  let totalEvents = 0

  let categorizedEvents = {
    ON_TIME: [],
    MEETS_SLO: [],
    MEETS_SLA: [],
    LATE: [],
    ERROR: [],
    NEW_EVT: [],
    NOT_REACHED_EXP: [],
    BREACHED_EXP: [],
  };

  events.forEach(event => {
    if (event.type === 'EVT' && categorizedEvents[event.outcomeStatus]) {
      categorizedEvents[event.outcomeStatus].push(event);
      totalEvents += 1
    }

    if (event.type === 'EXP') {
      if (event.plotStatus === 'NOT_REACHED') {
        categorizedEvents.NOT_REACHED_EXP.push(event)
      }
      else if (event.plotStatus === 'BREACHED') {
        categorizedEvents.BREACHED_EXP.push(event)
      }
    }
  });

  let expectationCount = totalEvents + categorizedEvents.NOT_REACHED_EXP.length + categorizedEvents.BREACHED_EXP.length ;

  return {
    summary: {
      totalEvents: totalEvents,
      totalExpectation: expectationCount,
      percentageComplete: expectationCount !== 0 ? (totalEvents / expectationCount) * 100 : 0,
    },
    eventStatus: {
      ON_TIME: categorizedEvents.ON_TIME.length,
      MEETS_SLO: categorizedEvents.MEETS_SLO.length,
      MEETS_SLA: categorizedEvents.MEETS_SLA.length,
      LATE: categorizedEvents.LATE.length,
      ERROR: categorizedEvents.ERROR.length,
      NEW_EVT: categorizedEvents.NEW_EVT.length,
      NOT_REACHED_EXP: categorizedEvents.NOT_REACHED_EXP.length,
      BREACHED_EXP: categorizedEvents.BREACHED_EXP.length,
    }
  };
};

export default CalculateMetrics;
