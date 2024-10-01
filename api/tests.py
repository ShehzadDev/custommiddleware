from django.urls import reverse
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from api.middlewares.logging import LoggingMiddleware
from api.middlewares.role_based_ratelimit import RateLimitMiddleware
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


class UserAuthTests(TestCase):
    def test_register_view(self):
        response = self.client.post(
            reverse("register"),
            {"email": "test@django.com", "password": "password", "role": "gold"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="test@django.com").exists())

    def test_login_view(self):
        user = User.objects.create_user(email="login@django.com", password="password")
        response = self.client.post(
            reverse("login"),
            {
                "email": user.email,
                "password": "password",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Login successful")

    def test_invalid_login(self):
        response = self.client.post(
            reverse("login"),
            {"email": "invalid@django.com", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid email or password")

    def test_logout_view(self):
        user = User.objects.create_user(email="logout@django.com", password="password")
        self.client.force_login(user)
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Logout successful")

    def test_protected_view_authenticated(self):
        user = User.objects.create_user(
            email="protected@django.com", password="password", role="gold"
        )
        self.client.force_login(user)
        response = self.client.get(reverse("protected"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Hello, protected@django.com", response.json()["message"])

    def test_protected_view_unauthenticated(self):
        response = self.client.get(reverse("protected"))
        self.assertEqual(response.status_code, 302)


class LoggingMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = LoggingMiddleware(get_response=lambda r: self.mock_view(r))

    def mock_view(self, request):
        from django.http import HttpResponse

        return HttpResponse("OK")

    def test_ip_logging_anonymous(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        response = self.middleware(request)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

    def test_ip_logging_authenticated(self):
        user = User.objects.create_user(email="test@django.com", password="password")
        request = self.factory.get("/")
        request.user = user
        response = self.middleware(request)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)


class RateLimitMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RateLimitMiddleware(get_response=lambda r: None)

    def test_rate_limit_unauthenticated(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        for _ in range(2):
            response = self.middleware(request)
        self.assertEqual(response.status_code, 429)

    def test_rate_limit_authenticated_gold(self):
        user = User.objects.create_user(
            email="gold@django.com", password="password", role="gold"
        )
        request = self.factory.get("/")
        request.user = user
        for _ in range(11):
            response = self.middleware(request)
        self.assertEqual(response.status_code, 429)

    def test_rate_limit_authenticated_silver(self):
        user = User.objects.create_user(
            email="silver@django.com", password="password", role="silver"
        )
        request = self.factory.get("/")
        request.user = user
        for _ in range(6):
            response = self.middleware(request)
        self.assertEqual(response.status_code, 429)
