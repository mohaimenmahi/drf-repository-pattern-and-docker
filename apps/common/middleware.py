from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import AuthenticationFailed
import jwt
from apps.users.repository import UserRepository
from apps.users.serializer import UserSerializer
from django.conf import settings

class TokenMiddleWare(MiddlewareMixin):
  user_repo = UserRepository()
  def process_request(self, request):
    token = request.COOKIES.get('access_token')
    
    # simply do nothing if token is not present
    if not token:
      return
    
    try:
      payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
      user_id = payload.get('user_id')
      phone_number = payload.get('phone_number')

      user = self.user_repo.get(id=user_id, phone_number=phone_number)
      if not user:
        raise AuthenticationFailed('User not found')
      
      request.user_id = user_id
    except jwt.ExpiredSignatureError:
      return
    except jwt.InvalidTokenError:
      return