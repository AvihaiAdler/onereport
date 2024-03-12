from typing import Self


class PersonnelDTO():
  def __init__(self: Self, id: str, first_name: str, last_name: str, company: str, platoon: str, active: bool = True, /) -> None:
    self.id = id
    self.first_name = first_name
    self.last_name = last_name
    self.company = company
    self.platoon = platoon
    self.active = active
    
  def __repr__(self: Self) -> str:
    return f"id: {self.id}, first_name: {self.first_name}, last_name: {self.last_name}, comapny: {self.company}, platoon: {self.platoon}, active: {str(self.active)}"
    