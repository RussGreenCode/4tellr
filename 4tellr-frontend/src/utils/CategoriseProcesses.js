// src/utils/CategoriseProcesses.js
import { useState, useEffect } from 'react';

const CategoriseProcesses = (events, setUpcomingProcesses, setOngoingProcesses, setJustFinishedProcesses) => {
  const now = new Date();
  const thirtyMinutesAgo = new Date(now.getTime() - 30 * 60000);
  const thirtyMinutesFuture = new Date(now.getTime() + 30 * 60000);

  const justFinishedProcesses = [];
  const ongoingProcesses = [];
  const upcomingProcesses = [];

  const eventsByName = events.reduce((acc, event) => {
    if (!acc[event.eventName]) {
      acc[event.eventName] = [];
    }
    acc[event.eventName].push(event);
    return acc;
  }, {});


  for (const eventName in eventsByName) {
    const eventGroup = eventsByName[eventName];
    const startedEvent = eventGroup.find(event => event.eventStatus === 'STARTED' && event.type === 'EVT');
    const successEvent = eventGroup.find(event => event.eventStatus === 'SUCCESS' && event.type === 'EVT');
    const expectedStartedEvent = eventGroup.find(event => event.eventStatus === 'STARTED'  && event.type === 'EXP');
    const expectedSuccessEvent = eventGroup.find(event => event.eventStatus === 'SUCCESS'  && event.type === 'EXP');

    if (startedEvent && successEvent) {
      const durationSeconds = (new Date(successEvent.TimeValue) - new Date(startedEvent.TimeValue)) / 1000;
      const process = {
        event_name: eventName,
        business_date: startedEvent.businessDate,
        start_time: startedEvent.TimeValue,
        expected_start_time: expectedStartedEvent ? expectedStartedEvent.TimeValue : null,
        end_time: successEvent.TimeValue,
        expected_end_time: expectedSuccessEvent ? expectedSuccessEvent.TimeValue : null,
        duration_seconds: durationSeconds,
        outcome: successEvent.plotStatus,
      };

      if (new Date(successEvent.TimeValue) >= thirtyMinutesAgo) {
        justFinishedProcesses.push(process);
      }
    } else if (startedEvent && !successEvent) {
      const expectedDurationSeconds = (new Date(expectedSuccessEvent.TimeValue) - new Date(expectedStartedEvent.TimeValue)) / 1000;
      const expectedEndTime = new Date(new Date(startedEvent.TimeValue).getTime() + expectedDurationSeconds * 1000);
      const process = {
        event_name: eventName,
        business_date: startedEvent.businessDate,
        start_time: startedEvent.TimeValue,
        expected_start_time: expectedStartedEvent ? expectedStartedEvent.TimeValue : null,
        end_time: expectedEndTime,
        expected_end_time: expectedSuccessEvent ? expectedSuccessEvent.TimeValue : null,
        duration_seconds: expectedDurationSeconds,
        outcome: startedEvent.plotStatus,
      };

      ongoingProcesses.push(process);
    } else if (!startedEvent && expectedStartedEvent && expectedSuccessEvent) {
      const expectedStartTime = new Date(expectedStartedEvent.TimeValue);
      const expectedEndTime = new Date(expectedSuccessEvent.TimeValue);

      if (expectedStartTime <= thirtyMinutesFuture) {
        const process = {
          event_name: eventName,
          business_date: expectedStartedEvent.businessDate,
          start_time: null,
          expected_start_time: expectedStartedEvent.TimeValue,
          end_time: null,
          expected_end_time: expectedSuccessEvent.TimeValue,
          duration_seconds: null,
          outcome: expectedStartedEvent.plotStatus,
        };

        upcomingProcesses.push(process);
      }
    }
  }

  setJustFinishedProcesses(justFinishedProcesses);
  setOngoingProcesses(ongoingProcesses);
  setUpcomingProcesses(upcomingProcesses);
};

export default CategoriseProcesses;
