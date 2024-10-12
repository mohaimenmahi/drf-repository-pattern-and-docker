from django.db import models
from apps.base.model import BaseModel

class User(BaseModel):
  email = models.EmailField(unique=True, blank=False, null=True)
  pin = models.CharField(max_length=255, blank=False, null=False)
  phone_number = models.CharField(unique=True, max_length=255, blank=False, null=False)
  name = models.CharField(max_length=255, blank=False, null=True)
  is_active = models.BooleanField(default=False)
  is_verified = models.BooleanField(default=False)

  class Meta:
    db_table = 'users'
    ordering = ['id']
    indexes = [
      models.Index(fields=['phone_number'], name='idx_phone_number'),
    ]
    verbose_name = 'User'
    verbose_name_plural = 'Users'

  def __str__(self):
    return f'{self.name}'
