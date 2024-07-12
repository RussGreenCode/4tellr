export const filterFavouriteEvents = (events, favouriteGroups) => {
  // Ensure favoriteGroups is an array
  if (!Array.isArray(favouriteGroups) || favouriteGroups.length === 0) {
    return events;
  }

  // Create a set of favourite group names for quick lookup
  const favouriteGroupSet = new Set(favouriteGroups.map(group => group.group_name));

  // Filter the events by checking if they belong to any of the favourite groups
  return events.filter(event => {
    if (!event.groups || !Array.isArray(event.groups)) {
      return false;
    }
    return event.groups.some(groupName => favouriteGroupSet.has(groupName));
  });
};
