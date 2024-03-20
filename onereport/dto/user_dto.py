from typing import Self
from onereport.data import misc
from onereport.data import model

class UserDTO():
  def __init__(self: Self, user: model.User) -> None:
    self.username = user.username
    self.email = user.email
    self.role = misc.Role[user.role].value
    self.company = misc.Company[user.company].value
    self.active = "פעיל" if user.active else "לא פעיל"
