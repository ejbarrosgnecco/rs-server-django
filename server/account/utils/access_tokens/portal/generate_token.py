import jwt
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

class NewAccessToken:
    def __init__ (self, user):
        self.user = user

    def generate_token(self):
        now = datetime.datetime.now()
        expiry = now.replace(hour=23, minute=59, second=0)
        expiry_time = (expiry - now).total_seconds()

        token_secret = os.environ.get("PORTAL_ACCESS_SECRET")
        encode_data = {
            "userId": str(self.user["_id"]),
            "emailAddress": self.user["emailAddress"],
            "firstName": self.user["firstName"],
            "lastName": self.user["lastName"],
            "organisation": {
                "_id": str(self.user["organisation"]["_id"]),
                "name": self.user["organisation"]["name"]
            },
            "team": {
                "_id": str(self.user["team"]["_id"]),
                "name": self.user["team"]["name"]
            },
            "profile": self.user["profile"],
            "role": self.user["role"],
            "exp": expiry_time
        }

        new_token = jwt.encode(encode_data, token_secret, "HS256")
        return {
            "accessToken": new_token,
            "expiresIn": expiry_time,
            "type": "Bearer"
        }