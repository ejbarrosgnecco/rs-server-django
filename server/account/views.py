from django.http import JsonResponse
from account.controllers.login import account_login

# Views
def login(request):
    match request.method:
        case "POST":
            response = account_login(email_address=request.json_body["emailAddress"], password=request.json_body["password"])
            return JsonResponse(response, status=200)
        case _:
            return JsonResponse({ "response_code": 404 }, status=404)