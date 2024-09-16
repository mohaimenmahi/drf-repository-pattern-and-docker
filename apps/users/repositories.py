from .models import User
from apps.base.repositories import BaseRepository

class UserRepository(BaseRepository):
  def __init__(self):
    super().__init__(User)

  def get_by_phone_number(self, phone_number):
    return self.filterOne(phone_number=phone_number)
  
  def get_all(self) -> list[User]:
    return self.filterAll()
  
  def get_by_id(self, id: int) -> User:
    return self.get(id=id)