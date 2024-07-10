# helpers/threshold.py
from datetime import timedelta

class Threshold:
    @staticmethod
    def get_sla_slo_thresholds(event_name, event_status):
        return {
            'on_time': timedelta(minutes=10),
            'slo': timedelta(minutes=30),
            'sla': timedelta(minutes=60)
        }
