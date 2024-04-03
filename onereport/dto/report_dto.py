from typing import Self
from onereport.data import misc, model
from onereport.dto.personnel_dto import PersonnelDTO

class ReportDTO():
  def __init__(self: Self, report: model.Report, personnel: list[model.Personnel], /) -> None:
    self.id = report.id
    self.date = report.date
    self.company = misc.Company[report.company].value
    self.presence = [(PersonnelDTO(p), p in report.presence) for p in personnel]
    
  def __repr__(self: Self) -> str:
    return "Report(id: {self.id}, date: {self.date}, company: {self.company})"