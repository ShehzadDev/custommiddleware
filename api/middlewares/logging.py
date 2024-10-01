import logging
import os
from datetime import datetime

request_logger = logging.getLogger("request_logger")


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.setup_logging()

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

    def setup_logging(self):
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"
        )
        log_file = os.path.join(log_dir, "requests.log")

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        if not request_logger.handlers:
            file_handler = logging.FileHandler(log_file)
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            request_logger.setLevel(logging.INFO)
            request_logger.addHandler(file_handler)
