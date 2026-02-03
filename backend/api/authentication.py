from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session authentication without CSRF enforcement for demo purposes"""
    
    def enforce_csrf(self, request):
        # Skip CSRF check - for demo only, not production!
        return
