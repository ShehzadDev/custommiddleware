import time
from collections import defaultdict
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class RateLimitMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response
        self.user_request_counts = defaultdict(
            lambda: {"count": 0, "timestamp": time.time(), "blocked": False}
        )
        super().__init__(get_response)

    def __call__(self, request):
        user_id = self.get_user_id(request)
        user_data = self.user_request_counts[user_id]
        current_time = time.time()

        if user_data["blocked"] and current_time - user_data["timestamp"] > 60:
            user_data["blocked"] = False
            user_data["count"] = 0
            user_data["timestamp"] = current_time

        if user_data["blocked"]:
            return JsonResponse(
                {
                    "error": "You are temporarily blocked due to too many requests. Try again in a minute."
                },
                status=429,
            )

        request_limit = self.get_request_limit()

        if current_time - user_data["timestamp"] > 60:
            user_data["count"] = 0
            user_data["timestamp"] = current_time

        user_data["count"] += 1

        if user_data["count"] > request_limit:
            user_data["blocked"] = True
            return JsonResponse(
                {"error": "Request limit exceeded. You are blocked for 1 minute."},
                status=429,
            )

        return self.get_response(request)

    def get_user_id(self, request):
        if request.user.is_authenticated:
            return request.user.id
        return self.get_client_ip(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")

    def get_request_limit(self):
        return 5
