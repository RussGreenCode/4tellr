from datetime import timedelta


class DatabaseHelperInterface:
    def insert_event(self, event_data):
        raise NotImplementedError

    def insert_event_outcome(self, outcome_data):
        raise NotImplementedError

    def query_events_by_date(self, business_date):
        raise NotImplementedError

    def query_events_by_date_for_chart(self, business_date):
        raise NotImplementedError

    def scan_events_last_month(self):
        raise NotImplementedError

    def query_event_details(self, event_id):
        raise NotImplementedError

    def calculate_expected_time(self, events):
        raise NotImplementedError

    def update_expected_times(self):
        raise NotImplementedError

    def get_expected_time(self, event_name, event_status):
        raise NotImplementedError

    def get_latest_metrics(self):
        raise NotImplementedError

    def generate_expectations(self, business_date):
        raise NotImplementedError

    def delete_expectations_for_business_date(self, business_date):
        raise NotImplementedError

    def delete_events_for_business_dates(self, business_dates):
        raise NotImplementedError

    def get_monthly_events(self, event_name, event_status):
        raise NotImplementedError

    def get_expectation_list(self):
        raise NotImplementedError

    def save_group(self, group_name, events, description):
        raise NotImplementedError

    def update_group(self, group_name, new_events):
        raise NotImplementedError

    def delete_group(self, group_name):
        raise NotImplementedError

    def get_all_groups(self):
        raise NotImplementedError

    def get_group_details(self, group_name):
        raise NotImplementedError

    def add_user(self, user):
        raise NotImplementedError

    def delete_user_by_email(self, email):
        raise NotImplementedError

    def get_all_users(self):
        raise NotImplementedError

    def get_user_by_email(self, email):
        raise NotImplementedError

    def validate_user(self, email, password):
        raise NotImplementedError

    def change_password(self, email, old_password, new_password):
        raise NotImplementedError

    def save_user_favourite_groups(self, email, favourite_groups):
        raise NotImplementedError

    def get_sla_slo_thresholds(self, event_name, event_status):
        raise NotImplementedError

    def get_plot_status(self, plot_type, outcome_status):
        raise NotImplementedError
