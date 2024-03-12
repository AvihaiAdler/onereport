from enum import Enum, auto

class Role(Enum):
  USER = auto()
  MANAGER = auto()
  ADMIN = auto()
  
class Space(Enum):
  A = auto()
  B = auto()
  C = auto()
  SUPPORT = auto()
  HEADQUARTERS = auto()