from typing import Self
from onereport.data import misc
from onereport.data import model

class PersonnelDTO():
  def __init__(self: Self, personnel: model.Personnel) -> None:
    self.id = personnel.id
    self.first_name = personnel.first_name
    self.last_name = personnel.last_name
    self.company = misc.Company[personnel.company].value
    # TODO: self.platoon
    self.active = "פעיל" if personnel.active else "לא פעיל"