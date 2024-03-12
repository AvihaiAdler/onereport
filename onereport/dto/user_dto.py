from typing import Self

class UserDTO():
  def __init__(self: Self, email: str, username: str, role: str, space: str, active: bool = True, /) -> None:
    self.email = email
    self.username = username
    self.role = role.lower()
    self.space = space.lower()
    self.active = active
    
  def __repr__(self: Self) -> str:
    return f"email: {self.email}, username: {self.username}, role: {self.role}, space: {self.space}, active: {str(self.active)}"
    