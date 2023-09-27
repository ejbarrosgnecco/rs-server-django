from server.utils.connection import get_mongo_connection
import bcrypt

user_collection = get_mongo_connection()["organisations"]["users"]

class ChangeOfPassword:
    def __init__ (self, org_id, user_id, current_password, new_password):
        self.org_id = org_id
        self.user_id = user_id
        self.current_password = current_password
        self.new_password = new_password
        self.user = None

    def get_user(self):    
        user = user_collection.find_one({ "_id": self.user_id, "organisation._id": self.org_id })

        if user:
            self.user = user

    def check_current_password(self):
        stored_bytes = self.password.encode("utf-8")
        user_bytes = self.current_password.encode("utf-8")

        password_match = bcrypt.checkpw(stored_bytes, user_bytes)
        return password_match

    def change_password(self):
        salt = bcrypt.gensalt()
        bytes = self.new_password.encode("utf-8")

        hash = bcrypt.hashpw(bytes, salt)

        user_collection.find_one_and_update({ "_id": self.user_id }, { "password": hash })
        return
def change_password(org_id: str, user_id: str, credentials: dict) -> dict:
    current_password = credentials["currentPassword"]
    new_password = credentials["newPassword"]

    password_change = ChangeOfPassword(
        org_id=org_id,
        user_id=user_id,
        current_password=current_password,
        new_password=new_password
    )

    # Check that user exists inside the database
    password_change.get_user()
    if password_change.user == None:
        return {
            "success": False,
            "reason": "User could not be found within organisation",
            "status": 404
        }

    # Check current password
    check_password = password_change.check_current_password()
    if check_password == False:
        return {
            "success": False,
            "reason": "This password is incorrect, please check and try again",
            "status": 400
        }

    # Encrypt and set new password
    try:
        password_change.change_password()
        return {
            "success": True,
            "status": 200
        }
    except Exception as e:
        print(e)
        return {
            "success": False,
            "reason": "Oops, there was a technical error, please try again",
            "status": 500
        }