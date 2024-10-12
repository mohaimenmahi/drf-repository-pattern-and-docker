from rest_framework.response import Response
from rest_framework import status
from apps.roles.repository import RoleRepository
from apps.base.service import BaseService
from .serializer import RoleSerializer
from apps.users.serializer import UserSerializer

class RoleService(BaseService):
  def __init__(self, role_repo: RoleRepository):
    self.role_repo = role_repo
  
  def get_all(self):
    try:
      roles = self.role_repo.get_all()
      roles = [role for role in roles if role.name != 'Admin']
      serializer = RoleSerializer(roles, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
      raise Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
  def get_by_id(self, id):
    try:
      role = self.role_repo.get_by_id(id)
      return Response(role, status=status.HTTP_200_OK)
    except Exception as e:
      raise Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
  def get_by_name(self, name):
    try:
      role = self.role_repo.get_by_name(name)
      if not role:
        raise Exception({'message':'Role not found'}, status=status.HTTP_404_NOT_FOUND)
      return Response(role, status=status.HTTP_200_OK)
    except Exception as e:
      raise Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
  def create_role(self, data):
    try:
      serializer = RoleSerializer(data=data)
      if serializer.is_valid():
        name = serializer.validated_data['name']
        role_exists = self.role_repo.get_by_name(name)
        if role_exists:
          raise Exception({'message': 'Role already exists'}, status=status.HTTP_409_CONFLICT)
        role = self.role_repo.create_role(name)
        return Response(role, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      raise Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
  def get_users_by_role(self, role_id):
    try:
      role = self.role_repo.get_users_by_role(role_id)
      if not role:
        raise Exception({'message': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
      users = role['users']
      serializer = UserSerializer(users, many=True)
      role['users'] = serializer.data
      return Response(role, status=status.HTTP_200_OK)
    except Exception as e:
      raise Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)