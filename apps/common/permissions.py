from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from apps.users.services import AuthService
from rest_framework.exceptions import AuthenticationFailed
from apps.users.repository import UserRepository
from apps.roles.repository import RoleRepository
from rest_framework import status

user_repo = UserRepository()
role_repo = RoleRepository()
auth_service =  AuthService(user_repo, role_repo)

class IsUserAuthenticated(BaseAuthentication):
  def authenticate(self, request):
    token = request.COOKIES.get('access_token')
    if not token:
      raise AuthenticationFailed('No token found')

    try:
      auth_service.validate_token(token)
      return None
    except Exception as e:
      raise AuthenticationFailed(str(e))
    
  def authenticate_header(self, request):
    return request
    
class HasRolePermission(BasePermission):
  def __init__(self, role=None):
    self.role = role

  @classmethod
  def with_role(cls, role):
    class RoleSpecificPermission(cls):
      def __init__(self):
        super().__init__(role=role)
        
    return RoleSpecificPermission

  def has_permission(self, request, view):
    user_id = request.user_id
    try:
      user = user_repo.get(id=user_id)
      if not user:
        return False
      return user.roles.filter(name=self.role).exists()
    except Exception as e:
      return False