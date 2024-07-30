export const DateTimeUtils = {

  parseTPlusTime(tPlusTime) {
    const regex = /^T\+(\d+)\s(\d{2}):(\d{2}):(\d{2})$/;
    const match = tPlusTime.match(regex);
    if (!match) throw new Error("Invalid T+ time format");

    const [, days, hours, minutes, seconds] = match.map(Number);
    return { days, hours, minutes, seconds };
  },

  formatTPlusTime(baseTime, additionalTime) {
    const totalSeconds = baseTime.seconds + additionalTime.seconds;
    const extraMinutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;

    const totalMinutes = baseTime.minutes + additionalTime.minutes + extraMinutes;
    const extraHours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;

    const totalHours = baseTime.hours + additionalTime.hours + extraHours;
    const extraDays = Math.floor(totalHours / 24);
    const hours = totalHours % 24;

    const days = baseTime.days + additionalTime.days + extraDays;

    return `T+${days} ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  },

   calculateTimeDifference(baseValueDateCalc, valueDateCalc) {
    const baseInSeconds = baseValueDateCalc.days * 24 * 3600 + baseValueDateCalc.hours * 3600 + baseValueDateCalc.minutes * 60 + baseValueDateCalc.seconds;
    const valueInSeconds = valueDateCalc.days * 24 * 3600 + valueDateCalc.hours * 3600 + valueDateCalc.minutes * 60 + valueDateCalc.seconds;

    const diffInSeconds = Math.abs(valueInSeconds - baseInSeconds);

    const diffDays = Math.floor(diffInSeconds / (24 * 3600));
    const remainingSecondsAfterDays = diffInSeconds % (24 * 3600);

    const diffHours = Math.floor(remainingSecondsAfterDays / 3600);
    const remainingSecondsAfterHours = remainingSecondsAfterDays % 3600;

    const diffMinutes = Math.floor(remainingSecondsAfterHours / 60);
    const diffSeconds = remainingSecondsAfterHours % 60;

    return { days: diffDays, hours: diffHours, minutes: diffMinutes, seconds: diffSeconds };
  },

  formatDifference({ days, hours, minutes, seconds }) {
    return `${days > 0 ? `T+${days} ` : ''}${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  },

  formatDifferenceFromStrings(daysStr, hoursStr, minutesStr, secondsStr) {
    const days = parseInt(daysStr, 10) || 0;
    const hours = parseInt(hoursStr, 10) || 0;
    const minutes = parseInt(minutesStr, 10) || 0;
    const seconds = parseInt(secondsStr, 10) || 0;

    return `${days > 0 ? `T+${days} ` : ''}${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  },

  addTimeToTPlus(baseValue, hoursToAdd, minutesToAdd) {
    const base = this.parseTPlusTime(baseValue);
    const additionalTime = {
      days: 0,
      hours: hoursToAdd,
      minutes: minutesToAdd,
      seconds: 0
    };
    return this.formatTPlusTime(base, additionalTime);
  },
};
