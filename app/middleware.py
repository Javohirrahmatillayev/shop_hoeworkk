from django.utils import timezone
from django.contrib.auth import logout 

class AutoLogoutAfterLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout_seconds = 60
        
    def __call__(self, request):
        if request.user.is_authenticated:
            now_ts = timezone.now().timestamp()
            login_ts = request.session.get('login_timestamp')
            
            if login_ts is None:
                request.session['login_timestamp'] = now_ts
            else:
                if (now_ts - float(login_ts)) > self.timeout_seconds:
                    logout(request)
                    request.session.pop('login_timestamp', None)
                    
        response = self.get_response(request)
        return response