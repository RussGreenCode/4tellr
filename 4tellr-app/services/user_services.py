import bcrypt

class UserServices:
    def __init__(self, db_helper, logger):
        self.db_helper = db_helper
        self.logger = logger

    def add_new_user(self, user):
        user['email'] = user.get('email', '').lower()
        email = user.get('email')

        if not email:
            return {'error': 'Email is required'}

        try:
            # Check if the user already exists
            response = self.db_helper.get_user_by_email(email)

            if response['success'] == False:

                # Initialise any other structure in the user here
                user['favourite_groups'] = []

                # Add the new user
                self.db_helper.add_user(user)
                return {'email': email, 'success': True, 'message': 'User added successfully'}
            else:
                return {'email': email, 'success': False, 'message': 'User with this email already exists'}

        except Exception as e:
            return {'email': email, 'success': False, 'error': str(e)}

    def delete_user_by_email(self, email):

        result = self.db_helper.delete_user_by_email(email)

        return result

    def get_all_users(self):

        response = self.db_helper.get_all_users()

        return response['data']

    def change_password(self, email, old_password, new_password):

        response = self.db_helper.get_user_by_email(email)

        user = response['data']

        if user and bcrypt.checkpw(old_password.encode('utf-8'), user['password'].encode('utf-8')):
            new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            result = self.db_helper.change_user_password(email, new_hashed_password)

            return result

        else:

            return {'success': False, 'message': 'Old password is incorrect'}


    def save_user_favourite_groups(self, email, favourite_groups):

        response = self.db_helper.save_user_favourite_groups(email, favourite_groups)

        return response

    def save_user_favourite_alerts(self, email, favourite_alerts):

        response = self.db_helper.save_user_favourite_alerts(email, favourite_alerts)

        return response

    def get_user_by_email(self, email):

        response = self.db_helper.get_user_by_email(email)

        return response['data']