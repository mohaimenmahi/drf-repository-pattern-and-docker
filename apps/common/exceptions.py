class AlreadyExistsError(Exception):
  def __init__(self, detail, code=409):
    self.detail = detail
    self.code = code