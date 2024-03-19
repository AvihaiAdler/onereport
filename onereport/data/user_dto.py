from typing import Self
from . import misc
from . import model

class UserDto():
  def __init__(self: Self, user: model.User) -> None:
    self.username = user.username
    self.email = user.email
    self.role = misc.Role[user.role].value
    self.company = misc.Space[user.company].value
    self.active = "פעיל" if user.active else "לא פעיל"
