from typing import Self


class UserEntity():
  def __init__(self: Self, username: str, role: str, space: str, active: bool = True, /) -> None:
    self.username = username
    self.role = role
    self.space = space
    self.active = active