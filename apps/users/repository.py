from .model import User
from apps.base.repository import BaseRepository

class UserRepository(BaseRepository):
  def __init__(self):
    super().__init__(User)

  def get_by_phone_number(self, phone_number):
    return self.filterOne(phone_number=phone_number)
  
  def get_all(self) -> list[User]:
    return self.filterAll()
  
  def get_by_id(self, id: int) -> User:
    return self.get(id=id)

  # prefetch_related is used to fetch the related objects in the same query, its for performance optimization
  # in many to many or many to one relationships to reduce the number of queries
  # select_related: same use, but for foreign key relationships/one-to-one relationships
  def get_user_with_roles(self, id: int) -> User:
    try:
      return self.model.objects.prefetch_related('roles').get(id=id)
    except self.model.DoesNotExist:
      return None
  