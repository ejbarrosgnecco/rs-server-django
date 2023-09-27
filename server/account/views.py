from django.http import JsonResponse, HttpResponseNotFound
import os
import json

# Middleware
from server.middleware.field_validation import field_validation_middleware
from server.middleware.route_access import validate_route_access

# Controllers
from account.controllers.login import account_login
from account.controllers.change_password import change_password

# Views
def login(request):
    match request.method:
        case "POST":
            validation_file = open(os.path.abspath("./account/field_validation/login.json"))
            data = json.load(validation_file)

            response = field_validation_middleware(
                func=account_login, 
                request_body=request.json_body,
                validation_file=data
            )( args=request.json_body )
            return JsonResponse(response, status=response["status"])
        case _:
            return HttpResponseNotFound()

@validate_route_access
def change_password(request):
    match request.method:
        case "PUT":
            validation_file = open(os.path.abspath("./account/field_validation/change_password.json"))
            data = json.load(validation_file)

            response = field_validation_middleware(
                func=change_password,
                request_body=request.json_body,
                validation_file=data
            )( 
                org_id=request.META["USER"]["organisation"]["_id"], 
                user_id=request.META["USER"]["userId"],
                credentials=request.json_body 
            )
            return JsonResponse(response, status=response["status"])
        case _:
            return HttpResponseNotFound()