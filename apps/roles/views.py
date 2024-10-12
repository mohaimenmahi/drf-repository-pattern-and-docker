from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from apps.common.permissions import IsAuthenticated, HasRolePermission
from apps.roles.repository import RoleRepository
from apps.roles.services import RoleService
from apps.roles.serializer import RoleSerializer
from apps.users.serializer import UserSerializer

role_repo = RoleRepository()
role_service = RoleService(role_repo)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_roles(request):
  reponse = role_service.get_all()
  return reponse

@api_view(['GET'])
@permission_classes([IsAuthenticated, HasRolePermission(role='admin')])
def get_roles_by_admin(request):
  response = role_service.get_all()
  return response

@api_view(['POST'])
@permission_classes([IsAuthenticated, HasRolePermission(role='admin')])
def create_role(request):
  data = request.data
  response = role_service.create_role(data)
  return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users_by_role(request, role_id):
  response = role_service.get_users_by_role(role_id)
  return response

