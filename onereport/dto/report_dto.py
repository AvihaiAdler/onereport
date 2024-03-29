from typing import Self
from onereport.data import misc, model
from onereport.dto import personnel_dto

class ReportDTO():
  def __init__(self: Self, report: model.Report) -> None:
    self.id = report.id
    self.date = report.date
    self.company = misc.Company[report.company].value
    self.presence = {personnel_dto.PersonnelDTO(personnel) for personnel in report.presence}
    
  def __repr__(self: Self) -> str:
    return "Report(id: {self.id}, date: {self.date}, company: {self.company})"