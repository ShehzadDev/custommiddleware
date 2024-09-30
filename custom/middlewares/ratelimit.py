import time
from django.core.exceptions import PermissionDenied


class RateLimitingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}

    def __call__(self, request):
        ip_address = self.get_client_ip(request)
        current_time = time.time()

        self.cleanup_requests(ip_address, current_time)

        if self.is_rate_limited(ip_address):
            raise PermissionDenied("Too many requests. Please try again later.")

        self.record_request(ip_address, current_time)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")

    def cleanup_requests(self, ip_address, current_time):

        if ip_address in self.requests:
            self.requests[ip_address] = [
                timestamp
                for timestamp in self.requests[ip_address]
                if current_time - timestamp < 60
            ]
            if not self.requests[ip_address]:
                del self.requests[ip_address]

    def is_rate_limited(self, ip_address):
        if ip_address in self.requests:
            return len(self.requests[ip_address]) >= 5
        return False

    def record_request(self, ip_address, current_time):
        if ip_address not in self.requests:
            self.requests[ip_address] = []
        self.requests[ip_address].append(current_time)
