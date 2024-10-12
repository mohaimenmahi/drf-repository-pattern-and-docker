import bcrypt
import jwt
from rest_framework.response import Response
from datetime import datetime
from django.conf import settings
from django.db import transaction
from rest_framework.exceptions import AuthenticationFailed
from apps.base.service import BaseService
from .repository import UserRepository
from apps.roles.repository import RoleRepository
from .serializer import UserSerializer
from apps.common.exceptions import AlreadyExistsError 
from rest_framework import status

class AuthService(BaseService):
    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository):
      self.user_repo = user_repo
      self.role_repo = role_repo

    def hash_pin(self, pin: str) -> str:
      salt = bcrypt.gensalt()
      hashed = bcrypt.hashpw(pin.encode('utf-8'), salt)
      return hashed.decode('utf-8')
    
    def verify_pin(self, pin: str, hashed_pin: str) -> bool:
      return bcrypt.checkpw(pin.encode('utf-8'), hashed_pin.encode('utf-8'))
    
    def register(self, data):
      serializer = UserSerializer(data=data)
      if not serializer.is_valid():
        raise Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
      phone_number = serializer.validated_data['phone_number']
      pin = serializer.validated_data['pin']
      name = serializer.validated_data['name']
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

      return Response(response, status=status.HTTP_201_CREATED)
    
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

        response = Response(responseUser, status=status.HTTP_200_OK)

        response.set_cookie(
          'access_token', 
          access_token, 
          httponly=settings.COOKIE_SETTINGS['HTTPONLY'],
          secure=settings.COOKIE_SETTINGS['SECURE'],
          samesite=settings.COOKIE_SETTINGS['SAMESITE']
        )
        response.set_cookie(
          'refresh_token', 
          refresh_token,
          httponly=settings.COOKIE_SETTINGS['HTTPONLY'],
          secure=settings.COOKIE_SETTINGS['SECURE'],
          samesite=settings.COOKIE_SETTINGS['SAMESITE']
        )      

        return response
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
          raise AuthenticationFailed(detail='User not found', status=status.HTTP_404_NOT_FOUND)
        return payload
      except jwt.ExpiredSignatureError:
        raise AuthenticationFailed(detail='Token has expired', status=status.HTTP_401_UNAUTHORIZED)
      except jwt.InvalidTokenError:
        raise AuthenticationFailed(details='Invalid token', status=status.HTTP_401_UNAUTHORIZED)
      
    def refresh_access_token(self, refresh_token: str) -> str:
      try:
        if not refresh_token:
          return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
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
        if not access_token:
          raise AuthenticationFailed('Invalid refresh token or credentials')

        response = Response({'access_token': access_token}, status=status.HTTP_200_OK)
        response.set_cookie(
          'access_token', 
          access_token,
          httponly=settings.COOKIE_SETTINGS['HTTPONLY'],
          secure=settings.COOKIE_SETTINGS['SECURE'],
          samesite=settings.COOKIE_SETTINGS['SAMESITE']
        )
        return response
      except Exception as e:
        raise Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
    def get_user_by_id(self, user_id):
      try:
        if not user_id:
          return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        user = self.user_repo.get_by_id(user_id)
        if not user:
          return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, fields=('id', 'phone_number', 'name', 'is_active', 'is_verified'))
        return Response(serializer.data, status=status.HTTP_200_OK)
      except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update_user_role(self, user_id, role_id):
      try:
        user = self.user_repo.get(id=user_id)
        if not user.role:
          role = self.role_repo.get(id=role_id)
          with transaction.atomic():
            user.roles.add(role)
            user.save()

            res = {
              'id': user.id,
              'phone_number': user.phone_number,
              'name': user.name,
              'is_active': user.is_active,
              'is_verified': user.is_verified,
              'roles': user.roles.all()
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
          raise Response({'message': 'User already has a role'}, status=status.HTTP_409_CONFLICT)
      except Exception as e:
        raise Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    