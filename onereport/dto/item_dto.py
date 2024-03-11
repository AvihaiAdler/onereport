from typing import Self

class ItemDTO():
  def __init__(self: Self, type: str, space: str, created_by: str, attributes: dict[str, str] = {}, /) -> None:
    self.type = type.lower()
    self.space = space.lower()
    self.created_by = created_by
    self.attributes = attributes
    