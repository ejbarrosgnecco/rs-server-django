from server.utils.connection import get_mongo_connection
from ..utils.access_tokens.portal.generate_token import NewAccessToken
import bcrypt

class AccountLoginAttempt:
    def __init__ (self, email_address, password):
        self.email_address = email_address
        self.password = password
        self.user = {}

    def get_user(self):
        user_collection = get_mongo_connection()["organisations"]["users"]
        user = user_collection.find_one({ "emailAddress": self.email_address })

        if user:
            self.user = user
            return True
        else:
            return False

    def check_password(self):
        stored_bytes = self.password.encode("utf-8")
        user_bytes = self.user["password"].encode("utf-8")
        
        password_match = bcrypt.checkpw(stored_bytes, user_bytes)
        print(password_match)

    def generate_access_token(self):
        new_token = NewAccessToken(self.user)
        return new_token.generate_token()


def account_login(email_address, password):
    login_attempt = AccountLoginAttempt(email_address=email_address, password=password)

    """ Check that user exists inside of database """
    user_found = login_attempt.get_user()
    if user_found == False:
        return {
            "success": False,
            "reason": "Incorrect email address or password combination, please try again"
        }

    """ Check that password matches """
    password_match = login_attempt.check_password()
    if password_match == False:
        return {
            "success": False,
            "reason": "Incorrect email address or password combination, please try again"
        }

    """ Generate access token """
    try:
        access_token = login_attempt.generate_access_token()
        return {
            "success": True,
            "data": access_token
        }
    except Exception as e:
        print(e)
        return {
            "success": False,
            "reason": "Oops, there was a technical error, please try again"
        }