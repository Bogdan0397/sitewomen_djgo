from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth import authenticate
from django.http import JsonResponse
import jwt



class JWTAuthenticationMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user = self.authenticate_user(token)
            if user:
                request.user = user
                return super().dispatch(request, *args, **kwargs)
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    def authenticate_user(self, token):

        pass