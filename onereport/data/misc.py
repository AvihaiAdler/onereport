from enum import Enum

class Role(Enum):
  USER = "פקיד"
  MANAGER = "שליש"
  ADMIN = "מנהל"
  
  @staticmethod
  def is_valid(role: str):
    return role in Role._member_names_
  
class Company(Enum):
  A = "פלוגה א"
  B = "פלוגה ב"
  C = "פלוגה ג"
  SUPPORT = "מסייעת"
  HEADQUARTERS = "מפקדה"
  
  @staticmethod
  def is_valid(company: str):
    return company in Company._member_names_