from typing import Self

class UserDTO():
  def __init__(self: Self, username: str, role: str, space: str, /) -> None:
    self.username = username
    self.role = role.lower()
    self.space = space.lower()
    