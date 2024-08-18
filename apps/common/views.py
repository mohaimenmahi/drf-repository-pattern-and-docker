from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

@api_view(['GET'])
def health(_request):
  return Response({'message': 'Server is up and running'}, status=status.HTTP_200_OK)