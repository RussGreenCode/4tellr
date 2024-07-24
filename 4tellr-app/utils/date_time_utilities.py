from datetime import datetime, timedelta


class DateTimeUtils:

    @staticmethod
    def calculate_time_difference(business_date: str, event_time_utc: str) -> timedelta:
        business_date_obj = datetime.fromisoformat(business_date)
        event_time_utc_obj = datetime.fromisoformat(event_time_utc)

        # Ensure both datetime objects are in UTC
        business_date_obj = business_date_obj.replace(tzinfo=event_time_utc_obj.tzinfo)

        time_diff = event_time_utc_obj - business_date_obj
        return time_diff

    @staticmethod
    def format_time_difference(business_date: str, event_time_utc: str) -> str:
        time_diff = DateTimeUtils.calculate_time_difference(business_date, event_time_utc)
        total_seconds = int(time_diff.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"T+{days} {hours:02}:{minutes:02}:{seconds:02}"

    @staticmethod
    def get_days_from_t_format(t_format: str) -> int:
        return int(t_format.split()[0][2:])

    @staticmethod
    def get_hours_from_t_format(t_format: str) -> int:
        return int(t_format.split()[1].split(':')[0])

    @staticmethod
    def get_minutes_from_t_format(t_format: str) -> int:
        return int(t_format.split()[1].split(':')[1])

    @staticmethod
    def get_seconds_from_t_format(t_format: str) -> int:
        return int(t_format.split()[1].split(':')[2])

    @staticmethod
    def calculate_event_time(business_date: str, t_format: str) -> str:
        business_date_obj = datetime.fromisoformat(business_date)
        days = DateTimeUtils.get_days_from_t_format(t_format)
        hours = DateTimeUtils.get_hours_from_t_format(t_format)
        minutes = DateTimeUtils.get_minutes_from_t_format(t_format)
        seconds = DateTimeUtils.get_seconds_from_t_format(t_format)
        event_time_obj = business_date_obj + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        return event_time_obj.isoformat()

    @staticmethod
    def convert_avg_time_to_t_format(avg_time_elapsed: str) -> str:
        hours, minutes, seconds = map(int, avg_time_elapsed.split(':'))
        total_seconds = hours * 3600 + minutes * 60 + seconds
        days = total_seconds // 86400
        remaining_hours = (total_seconds % 86400) // 3600
        remaining_minutes = (total_seconds % 3600) // 60
        remaining_seconds = total_seconds % 60
        return f"T+{days} {remaining_hours:02}:{remaining_minutes:02}:{remaining_seconds:02}"


# Example usage:
business_date = "2024-07-01T00:00:00+00:00"
event_time_utc = "2024-07-03T13:09:03+00:00"
avg_time_elapsed = "61:19:07"

print(DateTimeUtils.format_time_difference(business_date, event_time_utc))  # Output: T+2 13:09:03
print(DateTimeUtils.get_days_from_t_format("T+2 13:09:03"))  # Output: 2
print(DateTimeUtils.get_hours_from_t_format("T+2 13:09:03"))  # Output: 13
print(DateTimeUtils.get_minutes_from_t_format("T+2 13:09:03"))  # Output: 9
print(DateTimeUtils.get_seconds_from_t_format("T+2 13:09:03"))  # Output: 3
print(DateTimeUtils.calculate_event_time(business_date, "T+2 13:00:00"))  # Output: 2024-07-03T13:00:00+00:00
print(DateTimeUtils.convert_avg_time_to_t_format(avg_time_elapsed))  # Output: T+2 13:19:07
