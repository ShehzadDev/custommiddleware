from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from custom.middlewares.logging import LoggingMiddleware
from custom.middlewares.role_based_ratelimit import RateLimitMiddleware
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


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
