from typing import List
from onereport.data import model, misc
import sqlalchemy
import datetime

def find_report_by_date_and_company(date: datetime.date, company: misc.Company, /) -> model.Report | None:
  return model.db.session.scalar(sqlalchemy.select(model.Report).filter(model.Report.date == date).filter(model.Report.company == company.name))

def find_all_report_by_date(date: datetime.date, /) -> List[model.Report]:
  return model.db.session.scalars(sqlalchemy.select(model.Report).filter(model.Report.date == date).order_by(sqlalchemy.asc(model.Report.company))).all()