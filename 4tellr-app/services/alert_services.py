

class AlertServices:
    def __init__(self, db_helper, logger):
        self.db_helper = db_helper
        self.logger = logger

    def get_alert_details(self, alert_name):
        if alert_name is not None:

            result = self.db_helper.get_alert_details(alert_name)

            return result['data']

    def get_all_alerts(self):

        response = self.db_helper.get_all_alerts()

        return response['data']

    def save_alert(self, alert_name, description, group_name):
       
        if alert_name and group_name is not None:

           response = self.db_helper.save_alert(alert_name, description, group_name)
           return response

        else:
            print("[ERROR] 'alert_name' and 'group_name' must not be None.")
            return None

    def delete_alert(self, alert_name):
        if alert_name:
            response = self.db_helper.delete_alert(alert_name)

            return response
        else:
            print("[ERROR] 'alert_name' must not be None.")
            return None

    def update_alert(self, alert_name, description, group_name):

        if alert_name and group_name is not None:

            response = self.db_helper.update_alert(alert_name, description, group_name)
            return response

        else:
            print("[ERROR] 'alert_name' and 'group_name' must not be None.")
            return None
