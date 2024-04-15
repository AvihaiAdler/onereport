import datetime
from typing import Self
from onereport.data import misc, model
from onereport.dto.personnel_dto import PersonnelDTO
from onereport.dto.user_dto import UserDTO

class ReportDTO():
  def __init__(self: Self, report: model.Report, personnel: list[model.Personnel], /) -> None:
    self.id = report.id
    self.date = report.date
    self.company = misc.Company[report.company].value
    self.presence = [(PersonnelDTO(p), p in report.presence) for p in personnel] 
    self.edited_by = UserDTO(report.edited_by) if report.edited_by else ""
    self.last_edited = report.last_edited
    
  def __repr__(self: Self) -> str:
    return f"Report(id: {self.id}, date: {self.date}, company: {self.company})"
  
  
  
class UnifiedReportDTO():
  def __init__(self: Self, date: datetime.date, presence: set[model.Personnel], personnel: list[model.Personnel], /) -> None:
    self.date = date
    self.presence = [(PersonnelDTO(p), p in presence) for p in personnel]
    