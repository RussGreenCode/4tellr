// src/utils/filterFavouriteEvents.js
export const filterFavouriteEvents = (events, favouriteGroups) => {
  const favouriteEventSet = new Set();

  favouriteGroups.forEach(group => {
    group.events.forEach(event => favouriteEventSet.add(event));
  });

  return events.filter(event => favouriteEventSet.has(event.eventKey));
};
