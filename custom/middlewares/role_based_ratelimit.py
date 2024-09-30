import time
from collections import defaultdict
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


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
        limits = {
            "gold": 10,
            "silver": 5,
            "bronze": 2,
            "unauthenticated": 1,
        }
        return limits.get(role.lower(), 1)
