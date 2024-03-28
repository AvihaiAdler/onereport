from typing import Self
from onereport.data import misc
from onereport.data import model

class PersonnelDTO():
  def __init__(self: Self, personnel: model.Personnel) -> None:
    self.id = personnel.id
    self.first_name = personnel.first_name
    self.last_name = personnel.last_name
    self.company = misc.Company[personnel.company].value
    self.platoon = misc.Platoon[personnel.platoon].value
    self.active = "פעיל" if personnel.active else "לא פעיל"
    
  def __repr__(self: Self) -> str:
    return f"PersonnelDTO(id: {self.id}, first name: {self.first_name}, last name: {self.first_name}, company: {self.company}, platoon: {self.platoon}, active: {self.active})"