from django.http import HttpResponseForbidden
import jwt
import os
from dotenv import load_dotenv
from server.utils.connection import get_mongo_connection
from functools import reduce
from bson.objectid import ObjectId
import operator

load_dotenv()

class RouteValidation:
    def __init__ (self, access_token):
        self.access_token = access_token
        self.decoded_user = None
        self.user = None
        self.new_token = None

    def validate_token(self):
        decoded = jwt.decode(self.access_token, key=os.environ.get("PORTAL_ACCESS_SECRET"), algorithms=["HS256"], verify=True)
        self.decoded_user = decoded
        return

    def get_user(self):
        user_collection = get_mongo_connection()["organisations"]["users"]
        user = user_collection.find_one({ "_id": ObjectId(self.decoded_user["userId"]) })

        if user:
            self.user = user

    def value_check(self, key: str) -> bool:
        user_value = reduce(operator.getitem, key.split("."), self.decoded_user)
        
        if key == "userId":
            stored_value = self.user["_id"]
        else:
            stored_value = reduce(operator.getitem, key.split("."), self.user)    

        return str(user_value) == str(stored_value)

    def core_similarity_check(self) -> bool:
        core_checks = ["userId", "emailAddress", "organisation._id", "organisation.name"]
        return all(self.value_check(key=x) == True for x in core_checks)

def validate_route_access(func):
    def inner(*args, **kwargs):
        request = args[0].__dict__
        access_token = request["META"]["HTTP_AUTHORIZATION"]

        try:
            access_token = access_token.split(" ")[1]
            route_validation = RouteValidation(access_token=access_token)

            route_validation.validate_token()
            route_validation.get_user()
            
            if route_validation.user == None:
                return HttpResponseForbidden()

            core_check = route_validation.core_similarity_check()
            if core_check == False:
                return HttpResponseForbidden()

            # Not working - Try and fix
            #args[0].META["USER"] = route_validation.decoded_user

            return func(*args, **kwargs)

        except Exception as e:
            print(f"Route access line 69 - {e}")
            return HttpResponseForbidden()
            
    return inner