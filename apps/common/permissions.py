from rest_framework.permissions import BasePermission
from apps.users.services import AuthService
from rest_framework.exceptions import AuthenticationFailed
from apps.users.repositories import UserRepository
from rest_framework import status

user_repo = UserRepository()

auth_service =  AuthService(user_repo)

class IsAuthenticated(BasePermission):
  def has_permission(self, request, view):
    auth_service = AuthService(user_repo)
    
    token = request.COOKIES.get('access_token')
    if not token:
      return False
    
    try:
      auth_service.validate_token(token)
      return True
    except AuthenticationFailed as e:
      raise AuthenticationFailed(detail=str(e), code=status.HTTP_401_UNAUTHORIZED)