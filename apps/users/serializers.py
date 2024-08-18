from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = '__all__'
    
  def __init__(self, *args, **kwargs):
    fields = kwargs.pop('fields', None)

    super().__init__(*args, **kwargs)

    if fields is not None:
      allowed = set(fields) # fields that are allowed to be shown, given to the serializer into the argument
      existing = set(self.fields.keys()) # all fields in the serializer
      for field_name in existing - allowed:
        self.fields.pop(field_name)