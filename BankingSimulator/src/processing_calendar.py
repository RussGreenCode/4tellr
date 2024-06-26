from datetime import datetime

class ProcessingCalendar:
    def is_business_day(self, date):
        # Check if the date is a weekday (Monday to Friday)
        return date.weekday() < 5
