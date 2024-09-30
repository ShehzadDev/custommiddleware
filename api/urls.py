# urls.py
from django.urls import path
from .views import LoginView, LogoutView, RegisterView, ProtectedView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("protected/", ProtectedView.as_view(), name="protected"),
]
