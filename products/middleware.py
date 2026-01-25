from django.http import HttpResponseForbidden
from django.conf import settings

class AdminIPWhitelistMiddleware:
    """Only allow specific IPs to access admin panel"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # ✅ Add your office/home IP addresses here
        self.ALLOWED_IPS = getattr(settings, 'ADMIN_ALLOWED_IPS', [
            '127.0.0.1',  # Localhost
            # 'your.office.ip.address',  # Add manager's IP
        ])

    def __call__(self, request):
        # Check if accessing admin panel
        if request.path.startswith('/secure-manovastra-admin-2026/'):
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Allow if IP is whitelisted or in DEBUG mode
            if not settings.DEBUG and ip not in self.ALLOWED_IPS:
                return HttpResponseForbidden("Access Denied")
        
        return self.get_response(request)
