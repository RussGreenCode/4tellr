
const getEvtValue = (elements) => {
  const expElement = elements.find(element => element.type === 'EXP');
  const evtElement = elements.find(element => element.type === 'EVT');

  if (!evtElement && expElement) {
    return new Date(expElement.expectationTime).getTime();
  }
  if (evtElement && expElement) {
    return new Date(evtElement.time).getTime();
  }
  if (evtElement && !expElement) {
    return new Date(evtElement.time).getTime();
  }
};

const getExpValue = (elements) => {
  const expElement = elements.find(element => element.type === 'EXP');
  const evtElement = elements.find(element => element.type === 'EVT');

  if (!evtElement && expElement) {
    return new Date(expElement.expectationTime).getTime();
  }
  if (expElement && evtElement) {
    return new Date(expElement.expectationTime).getTime();
  }
  if (evtElement && !expElement) {
    return new Date(evtElement.time).getTime();
  }
};

const generateYCoordinateIndexMap = (data, sortCriterion) => {
  const yCoordinateIndexMap = {};

  // Initialize the map with unique yCoordinates
  data.flatMap(item => item.data).forEach(item => {
    if (!yCoordinateIndexMap[item.yCoordinate]) {
      yCoordinateIndexMap[item.yCoordinate] = {
        yCoordinate: item.yCoordinate,
        exp_time_value: null,
        exp_index: null,
        evt_time_value: null,
        evt_index: null
      };
    }
  });

  // Populate exp_time_value and evt_time_value
  Object.keys(yCoordinateIndexMap).forEach(yCoordinate => {
    const elements = data.flatMap(item => item.data).filter(item => item.yCoordinate === yCoordinate);

    yCoordinateIndexMap[yCoordinate].exp_time_value = getExpValue(elements);
    yCoordinateIndexMap[yCoordinate].evt_time_value = getEvtValue(elements);
  });

  // Assign indices based on sorted time values
  const expSorted = Object.values(yCoordinateIndexMap).sort((a, b) => a.exp_time_value - b.exp_time_value);
  expSorted.forEach((item, index) => {
    item.exp_index = index;
  });

  const evtSorted = Object.values(yCoordinateIndexMap).sort((a, b) => a.evt_time_value - b.evt_time_value);
  evtSorted.forEach((item, index) => {
    item.evt_index = index;
  });

  return yCoordinateIndexMap;
};

export { generateYCoordinateIndexMap, getEvtValue, getExpValue };