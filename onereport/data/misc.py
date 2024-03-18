from enum import Enum

class Role(Enum):
  USER = "פקיד"
  MANAGER = "שליש"
  ADMIN = "מנהל"
  
class Space(Enum):
  A = "פלוגה א"
  B = "פלוגה ב"
  C = "פלוגה ג"
  SUPPORT = "מסייעת"
  HEADQUARTERS = "מפקדה"