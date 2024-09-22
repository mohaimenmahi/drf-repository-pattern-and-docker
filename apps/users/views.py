from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from apps.common.permissions import IsAuthenticated
from apps.users.services import AuthService
from apps.users.repositories import UserRepository

user_repo = UserRepository()
auth_service = AuthService(user_repo)

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
@permission_classes([IsAuthenticated])
def get_user(request, id):
  response = auth_service.get_user_by_id(id)
  return response
  
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
  user_id = request.user_id
  response = auth_service.get_user_by_id(user_id)
  return response