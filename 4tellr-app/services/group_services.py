

class GroupServices:
    def __init__(self, db_helper, logger):
        self.db_helper = db_helper
        self.logger = logger

    def get_group_details(self, group_name):
        if group_name is not None:

            result = self.db_helper.get_group_details(group_name)

            return result['data']

    def get_all_groups(self):

        response = self.db_helper.get_all_groups()

        return response['data']

    def save_group(self, group_name, events, description):
        if group_name and events is not None:

           response = self.db_helper.save_group(group_name, events, description)
           return response

        else:
            print("[ERROR] 'group_name' and 'events' must not be None.")
            return None

    def delete_group(self, group_name):
        if group_name:
            response = self.db_helper.delete_group(group_name)

            return response
        else:
            print("[ERROR] 'group_name' must not be None.")
            return None


    def get_group_details(self, group_name):
        if group_name is not None:

            response = self.db_helper.get_group_details(group_name)
            return response['data']

        else:
            print("[ERROR] 'group_name' must not be None.")
            return None