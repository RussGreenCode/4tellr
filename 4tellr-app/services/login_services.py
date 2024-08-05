
class LoginServices:
    def __init__(self, db_helper,logger):
        self.db_helper = db_helper
        self.logger = logger

    def get_user_by_email(self, email):
        try:
            response = self.db_helper.get_user_by_email(email)
            return response['data']
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
