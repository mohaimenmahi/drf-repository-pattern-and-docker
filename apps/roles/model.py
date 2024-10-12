from django.db import models
from apps.base.model import BaseModel

class Role(BaseModel):
  name = models.CharField(max_length=255, blank=False, null=False)
  
  class Meta:
    db_table = 'roles'
    ordering = ['id']
  
  def __str__(self):
    return self.name