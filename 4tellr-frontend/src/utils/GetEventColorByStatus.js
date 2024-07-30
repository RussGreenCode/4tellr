

export const getEventColorByStatus = (status) => {
    return status === 'NEW' ? 'blue'
      : status === 'ON_TIME' ? 'darkgreen'
      : status === 'MEETS_SLO' ? 'lightgreen'
      : status === 'MEETS_SLA' ? 'orange'
      : status === 'MET_THRESHOLD' ? 'darkgreen'
      : status === 'BREACHED' ? 'red'
      : status === 'NOT_REACHED' ? 'grey'
      : status === 'LATE' ? 'red'
      : 'darkred';
  };