from enum import Enum

class Role(Enum):
  USER = "פקיד"
  MANAGER = "שליש"
  ADMIN = "מנהל"
  
  @staticmethod
  def is_valid(role: str, /) -> bool:
    return role in Role._member_names_
  
class Company(Enum):
  A = "פלוגה א"
  B = "פלוגה ב"
  C = "פלוגה ג"
  SUPPORT = "מסייעת"
  HEADQUARTERS = "מפקדה"
  
  @staticmethod
  def is_valid(company: str, /) -> bool:
    return company in Company._member_names_
  
class Platoon(Enum):
  UNCATEGORIZED = "לא משוייך"
  FIRST = "1"
  SECOND = "2"
  THIRD = "3"
  FORTH = "4"
  FIFTH = "5"
  SIXTH = "6"
  SEVENTH = "7"
  EIGHTH = "8"
  NINTH = "9"
  
  @staticmethod
  def is_valid(platoon: str, /) -> bool:
    return platoon in Platoon._member_names_  

class Active(Enum):
  ACTIVE = "פעיל"
  INACTIVE = "לא פעיל"
  
  @staticmethod
  def is_valid(active: str, /) -> bool:
    return active in Active._member_names_ 
  
class Presence(Enum):
  PRESENT = "נמצא"
  NOT_PRESENT = "לא נמצא"
  
  @staticmethod
  def is_valid(presence: str, /) -> bool:
    return presence in Presence._member_names_