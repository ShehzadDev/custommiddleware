import logging
from datetime import datetime
import time
from collections import defaultdict
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

request_logger = logging.getLogger("request_logger")


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = self.get_client_ip(request)

        user = request.user.email if request.user.is_authenticated else "Anonymous"
        request_time = datetime.now()

        request_logger.info(
            f"IP: {ip_address}, User: {user}, Request Time: {request_time}"
        )

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        return (
            x_forwarded_for.split(",")[0]
            if x_forwarded_for
            else request.META.get("REMOTE_ADDR")
        )


class RateLimitMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response
        self.user_request_counts = defaultdict(
            lambda: {"count": 0, "timestamp": time.time()}
        )
        super().__init__(get_response)

    def __call__(self, request):
        user_role = self.get_user_role(request)
        request_limit = self.get_request_limit(user_role)

        current_time = time.time()
        user_id = self.get_user_id(request)

        if current_time - self.user_request_counts[user_id]["timestamp"] > 60:
            self.user_request_counts[user_id]["count"] = 0
            self.user_request_counts[user_id]["timestamp"] = current_time

        self.user_request_counts[user_id]["count"] += 1

        if self.user_request_counts[user_id]["count"] > request_limit:
            return JsonResponse(
                {"error": "Request limit exceeded. Try again later."}, status=429
            )

        response = self.get_response(request)
        return response

    def get_user_role(self, request):
        if request.user.is_authenticated:
            return request.user.role
        return "unauthenticated"

    def get_user_id(self, request):
        if request.user.is_authenticated:
            return request.user.id
        return self.get_client_ip(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def get_request_limit(self, role):
        return settings.ROLE_REQUEST_LIMITS.get(role.lower(), 1)
