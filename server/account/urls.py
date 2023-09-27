from django.urls import path
from . import views

urlpatterns = [
    path("login", views.login, name="Account login"),
    path("change-password", views.change_password, name="Change password")
]