from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import AuthenticationFailed
import jwt
from apps.users.repositories import UserRepository
from apps.users.serializers import UserSerializer
from django.conf import settings

class TokenMiddleWare(MiddlewareMixin):
  user_repo = UserRepository()

  def process_request(self, request):
    token = request.COOKIES.get('access_token') if settings.ENV == 'production' else request.headers.get('access_token')

    # simply do nothing if token is not present
    if not token:
      return
    
    try:
      payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
      user_id = payload['user_id']

      user = self.user_repo.get_by_id(user_id)
      if not user:
        raise AuthenticationFailed('User not found')
      
      request.user = UserSerializer(user, fields=('id', 'phone_number', 'name', 'is_active', 'is_verified')).data
    except jwt.ExpiredSignatureError:
      raise AuthenticationFailed('Token expired')
    except jwt.InvalidTokenError:
      raise AuthenticationFailed('Invalid token')