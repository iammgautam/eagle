from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)

class IPLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        logger.info(f"Request from IP: {ip}")