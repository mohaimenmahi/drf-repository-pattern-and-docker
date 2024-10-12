from apps.base.repository import BaseRepository
from .model import Role

class RoleRepository(BaseRepository):
  def __init__(self):
    super().__init__(Role)
  
  def get_all(self):
    return self.filterAll()
  
  def get_by_id(self, id):
    return self.get(id=id)
  
  def get_by_name(self, name):
    return self.filterOne(name=name)
  
  def create_role(self, name):
    role = self.create(name=name)
    role.save()
    return role
  
  def get_users_by_role(self, role_id):
    role = self.get(id=role_id)
    if not role:
      return None
    
    users = role.users.all()

    res = {
      'id': role.id,
      'name': role.name,
      'users': users
    }
    
    return res