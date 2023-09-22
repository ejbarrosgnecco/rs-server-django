from django.shortcuts import render, HttpResponse
from account.controllers.login import account_login

# Create your views here.
def login(request):
    return HttpResponse("Hello, world!")