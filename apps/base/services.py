class BaseService:
  def __init__(self, repository):
    self.repository = repository
  
  def get(self, **kwargs):
    return self.repository.get(**kwargs)
  
  def filter(self, **kwargs):
    return self.repository.filter(**kwargs)
  
  def create(self, **kwargs):
    return self.repository.create(**kwargs)
  
  def update(self, id, **kwargs):
    return self.repository.update(id, **kwargs)
  
  def delete(self, id):
    return self.repository.delete(id)