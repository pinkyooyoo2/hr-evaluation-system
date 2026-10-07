from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        # Exempt CSRF for SPA cross-origin requests; security is maintained via CORS allowed origins
        return
