from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from apps.common.permissions import IsUserAuthenticated, HasRolePermission
from apps.users.services import AuthService
from apps.users.repository import UserRepository
from apps.roles.repository import RoleRepository

user_repo = UserRepository()
role_repo = RoleRepository()
auth_service = AuthService(user_repo, role_repo)

# Register user
@api_view(['POST'])
def register(request):
  data = request.data
  user = auth_service.register(data)
  return user

# Login user
@api_view(['POST'])
def login(request):
  data = request.data
  response = auth_service.login(data['phone_number'], data['pin'])
  return response

# Logout user
@api_view(['POST'])
def logout(request):
  response = Response(status=status.HTTP_200_OK)
  response.delete_cookie('access_token')
  response.delete_cookie('refresh_token')

  return response
  
# Refresh Access token
@api_view(['POST'])
def refresh_access_token(request):
  refresh_token = request.COOKIES.get('refresh_token')
  response = auth_service.refresh_access_token(refresh_token)
  return response

# Get a single user
@api_view(['GET'])
@authentication_classes([IsUserAuthenticated])
def get_user(request, id):
  response = auth_service.get_user_by_id(id)
  return response

# get current use session 
@api_view(['GET'])
@authentication_classes([IsUserAuthenticated])
def get_current_user(request):
  print('userId', request.user_id)
  user_id = request.user_id
  response = auth_service.get_user_by_id(user_id)
  return response
  
@api_view(['PUT'])
@authentication_classes([IsUserAuthenticated])
@permission_classes([HasRolePermission(role='Admin')])
def update_user_role(request):
  data = request.data
  user_id = data['user_id']
  role_id = data['role_id']
  res = auth_service.update_user_role(user_id, role_id)
  return res
  
@api_view(['PUT'])
@authentication_classes([IsUserAuthenticated])
def update_self_role(request):
  data = request.data
  user_id = request.user_id
  role_id = data['role_id']
  res = auth_service.update_user_role(user_id, role_id)
  return res