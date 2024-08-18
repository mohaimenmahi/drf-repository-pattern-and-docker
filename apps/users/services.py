import bcrypt
import jwt
from datetime import datetime
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from .repositories import UserRepository
from .serializers import UserSerializer
from .models import User
from apps.common.exceptions import AlreadyExistsError 

class AuthService:
    def __init__(self, user_repo: UserRepository):
      self.user_repo = user_repo

    def hash_pin(self, pin: str) -> str:
      salt = bcrypt.gensalt()
      hashed = bcrypt.hashpw(pin.encode('utf-8'), salt)
      return hashed.decode('utf-8')
    
    def verify_pin(self, pin: str, hashed_pin: str) -> bool:
      return bcrypt.checkpw(pin.encode('utf-8'), hashed_pin.encode('utf-8'))
    
    def register(self, phone_number, pin, name):
      user = self.user_repo.get_by_phone_number(phone_number)
      if user:
        raise AlreadyExistsError(detail='User already exists', code=409)
      
      hashed_pin = self.hash_pin(pin)
      user_data = {
        'phone_number': phone_number,
        'pin': hashed_pin,
        'name': name,
        'is_active': True,
        'is_verified': False
      }

      user = self.user_repo.create(**user_data)

      response = UserSerializer(user, fields=('id', 'phone_number', 'name', 'is_active', 'is_verified')).data

      return response
    
    def login(self, phone_number, pin):
      user = self.user_repo.get_by_phone_number(phone_number)

      if not user.is_active:
        raise AuthenticationFailed('User is inactive')
      
      if not user.is_verified:
        raise AuthenticationFailed('User is not verified')
      
      if user and self.verify_pin(pin, user.pin):
        access_token = self.generate_access_token(user)
        refresh_token = self.generate_refresh_token(user)

        responseUser = UserSerializer(user, fields=('id', 'phone_number', 'name', 'is_active', 'is_verified')).data

        return {
          'user': responseUser,
          'access_token': access_token,
          'refresh_token': refresh_token
        }
      
      raise AuthenticationFailed('Invalid credentials')
    
    def generate_access_token(self, user):
      payload = {
        'user_id': user.id,
        'phone_number': user.phone_number,
        'exp': datetime.now() + settings.JWT_SETTINGS.get('ACCESS_TOKEN_LIFETIME'),
        'iat': datetime.now()
      }

      return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    def generate_refresh_token(self, user):
      payload = {
        'user_id': user.id,
        'phone_number': user.phone_number,
        'exp': datetime.now() + settings.JWT_SETTINGS.get('REFRESH_TOKEN_LIFETIME'),
        'iat': datetime.now()
      }

      return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    def validate_token(self, token):
      try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        user_id = payload.get('user_id')
        phone_number = payload.get('phone_number')
        user = self.user_repo.get(id=user_id, phone_number=phone_number)
        if not user:
          raise AuthenticationFailed('User not found')
        return payload
      except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired')
      except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')
      
    def refresh_access_token(self, refresh_token: str) -> str:
      payload = self.validate_token(refresh_token)

      # If refresh token is not valid, raise an exception, need to login again
      if not payload:
        raise AuthenticationFailed('Invalid token')
    
      # refresh token is valid and we can now generate a new access token without login again
      user_id = payload.get('user_id')
      phone_number = payload.get('phone_number')

      user = self.user_repo.get(id=user_id, phone_number=phone_number)

      if user is None:
        raise AuthenticationFailed('User not found')
    
      access_token = self.generate_access_token(user)
      
      return access_token
    