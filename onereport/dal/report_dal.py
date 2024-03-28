from onereport.dal import order_attr
from onereport.data import model, misc
import sqlalchemy
import datetime

def find_report_by_id(id: int, /) -> model.Report | None:
  return model.db.session.scalar(sqlalchemy.select(model.Report).filter(model.Report.id == id))

def find_report_by_id_and_company(id: int, company: misc.Company, /) -> model.Report | None:
  return model.db.session.scalar(sqlalchemy.select(model.Report).filter(model.Report.id == id).filter(model.Report.company == company.name))

def find_report_by_date_and_company(date: datetime.date, company: misc.Company, /) -> model.Report | None:
  return model.db.session.scalar(sqlalchemy.select(model.Report).filter(model.Report.date == date).filter(model.Report.company == company.name))

def find_all_reports_by_company(company: misc.Company, order: order_attr.Order, /) -> list[model.Report]:
  return model.db.session.scalars(
    sqlalchemy.select(model.Report)
              .filter(model.Report.company == company.name)
              .order_by(sqlalchemy.asc(model.Report.date) if order == order_attr.Order.ASC else sqlalchemy.desc(model.Report.date))
    ).all()