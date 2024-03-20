from enum import Enum


class Order(Enum):
  ASC = "asc"
  DESC = "desc"
  
  @staticmethod
  def is_valid_order(order: str) -> bool:
    return order in Order._member_names_
  
class UserOrderBy(Enum):
  EMAIL = "email"
  USERNAME = "username"
  COMPANY = "company"
  
  @staticmethod
  def is_valid_order(order: str) -> bool:
    return order in UserOrderBy._member_names_
  
class PersonnelOrderBy(Enum):
  ID = "id"
  FIRST_NAME = "first_name"
  LAST_NAME = "last_name"
  COMPANY = "company"
  PLATOON = "platton"
  
  @staticmethod
  def is_valid_order(order: str) -> bool:
    return order in PersonnelOrderBy._member_names_
  