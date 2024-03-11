from typing import Self
import uuid


class ItemEntity():
  def __init__(self: Self, id: uuid, type: str, space: str, created_at: str, active: bool = True, attributes: dict[str, str] = {}, /) -> None:
    self.id = id
    self.type = type
    self.space = space
    self.created_at = created_at
    self.active = active
    self.attributes = attributes