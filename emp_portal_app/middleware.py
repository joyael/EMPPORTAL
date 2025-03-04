from django.utils.deprecation import MiddlewareMixin
import user_agents

class SessionTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            session = request.session
            if 'ip' not in session:
                session['ip'] = request.META.get('REMOTE_ADDR', 'Unknown IP')
            if 'browser' not in session:
                ua = user_agents.parse(request.META.get('HTTP_USER_AGENT', ''))
                session['browser'] = f"{ua.browser.family} {ua.browser.version_string}"
            if 'device' not in session:
                session['device'] = ua.device.family
            session.save()
