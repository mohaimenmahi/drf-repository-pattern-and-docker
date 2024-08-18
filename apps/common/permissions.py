from rest_framework.permissions import BasePermission
from apps.users.services import AuthService
from rest_framework.exceptions import AuthenticationFailed
from apps.users.repositories import UserRepository
from django.conf import settings

user_repo = UserRepository()

class IsAuthenticated(BasePermission):
  def has_permission(self, request, view):
    auth_service = AuthService(user_repo)
    
    token = request.COOKIES.get('access_token') if settings.ENV == 'production' else request.headers.get('access_token')

    if not token:
      return False
    
    try:
      auth_service.validate_token(token)
      return True
    except AuthenticationFailed:
      return False