import bcrypt
from flask import current_app

class UserHelper():
    def __init__(self):
        pass

    @property
    def db_helper(self):
        return current_app.config['DB_HELPER']

    def add_new_user(self, user):
        user['email'] = user.get('email', '').lower()
        email = user.get('email')

        if not email:
            return {'error': 'Email is required'}

        try:
            # Check if the user already exists
            response = self.db_helper.get_user_by_email(email)

            if response['success'] == False:
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