"""
Custom middleware for the GreenBridge application.
"""
import time
from django.utils.deprecation import MiddlewareMixin


class PrometheusMiddleware(MiddlewareMixin):
    """
    Middleware to collect metrics for Prometheus.
    This captures request/response metrics such as latency, status codes, etc.
    """
    
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        # Only measure if we have start_time
        if hasattr(request, 'start_time'):
            # Response time in milliseconds
            latency = (time.time() - request.start_time) * 1000
            
            # In a real implementation, we would use prometheus_client to export metrics
            # For now, we'll just add the latency to the response headers for logging
            response['X-Response-Time-ms'] = str(int(latency))
        
        return response 