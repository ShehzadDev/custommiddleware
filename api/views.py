from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

User = get_user_model()


class RegisterView(View):
    def get(self, request):
        return render(request, "register.html")

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role", "default")

        if role == "default":
            role = "default"

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        user = User(email=email, role=role)
        user.set_password(password)
        user.save()

        messages.success(request, "Registration successful. You can now log in.")
        return redirect("login")


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("protected")
        return render(request, "login.html")

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            return JsonResponse(
                {"error": "Email and password are required."}, status=400
            )

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({"message": "Login successful"})
        else:
            return JsonResponse({"error": "Invalid email or password"}, status=400)


class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
            return JsonResponse({"message": "Logout successful"})
        else:
            return JsonResponse({"error": "You are not logged in"}, status=400)


@method_decorator(login_required, name="dispatch")
class ProtectedView(View):
    def get(self, request):
        return JsonResponse(
            {
                "message": f"Hello, {request.user.email}. This is a protected view. Your role is {request.user.role}."
            }
        )
