from typing import Type, TypeVar
from django.db import models

T = TypeVar('T', bound=models.Model)

class BaseRepository:
  def __init__(self, model: Type[T]):
    self.model = model

  def get(self, **kwargs) -> T:
    return self.model.objects.get(**kwargs)

  def filter(self, **kwargs) -> list[T]:
    return self.model.objects.filter(**kwargs)

  def create(self, **kwargs) -> T:
    return self.model.objects.create(**kwargs)

  def update(self, id: int, **kwargs) -> None:
    self.model.objects.filter(id=id).update(**kwargs)

  def delete(self, id: int) -> None:
    self.model.objects.filter(id=id).delete()