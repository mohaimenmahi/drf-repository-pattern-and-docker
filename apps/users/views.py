from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from apps.common.permissions import IsAuthenticated
from apps.users.services import AuthService
from apps.users.repositories import UserRepository
from apps.users.serializers import UserSerializer
from apps.common.exceptions import AlreadyExistsError 

user_repo = UserRepository()
auth_service = AuthService(user_repo)

# Register user
@api_view(['POST'])
def register(request):
  data = request.data
  print(data)
  serializer = UserSerializer(data=data)
  print(serializer.is_valid())
  if serializer.is_valid():
    try:
      phone_number = serializer.validated_data['phone_number']
      pin = serializer.validated_data['pin']
      name = serializer.validated_data['name']
      
      user = auth_service.register(phone_number, pin, name)

      return Response(user, status=status.HTTP_201_CREATED)
    except AlreadyExistsError as e:
      return Response({'message': e.detail}, status=status.HTTP_409_CONFLICT)
    except Exception as e:
      return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
  return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login user
@api_view(['POST'])
def login(request):
  data = request.data

  try:
    login_data = auth_service.login(data['phone_number'], data['pin'])
    response = Response(login_data, status=status.HTTP_200_OK)
    response.set_cookie('access_token', login_data['access_token'], httponly=True)
    response.set_cookie('refresh_token', login_data['refresh_token'], httponly=True)

    return response
  except Exception as e:
    return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Logout user
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
  try:
    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')

    return response
  except Exception as e:
    return Response(e.detail, status=e.code)
  
# Refresh Access token
@api_view(['POST'])
def refresh_access_token(request):
  try:
    refresh_token = request.COOKIES.get('refresh_token')
    if not refresh_token:
      return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    access_token = auth_service.refresh_access_token(refresh_token)
    response = Response({'access_token': access_token}, status=status.HTTP_200_OK)
    response.set_cookie('access_token', access_token, httponly=True)

    return response
  except Exception as e:
    return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Get a single user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request, id):
  try:
    user = user_repo.get_by_id(id)
    if not user:
      return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserSerializer(user, fields=('id', 'phone_number', 'name', 'is_active', 'is_verified'))
    return Response(serializer.data, status=status.HTTP_200_OK)
  except Exception as e:
    return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)