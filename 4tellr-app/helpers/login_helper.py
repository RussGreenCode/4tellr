from flask import current_app

class LoginHelper():
    def __init__(self):
        pass

    @property
    def db_helper(self):
        return current_app.config['DB_HELPER']

    def get_user_by_email(self, email):
        try:
            response = self.db_helper.get_user_by_email(email)
            return response['data']
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
