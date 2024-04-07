from onereport import app
from onereport.dal import order_attr
from onereport.data import model, misc
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
import datetime

def save(report: model.Report, /) -> bool:
    if report is None:
        return False
    
    try:
        model.db.session.add(report)
        model.db.session.commit()
    except SQLAlchemyError as se:
      app.logger.error(f"{se}")
      model.db.session.rollback()
      return False 
    return True


def update(report: model.Report, presence: set[model.Personnel], /) -> bool:
    if report is None:
        return False
    
    try:
        report.update(presence)
        model.db.session.commit()
    except SQLAlchemyError as se:
      app.logger.error(f"{se}")
      model.db.session.rollback()
      return False 
    return True


def save_all(reports: list[model.Report], /) -> bool:
    if reports is None or not reports:
        return False
    
    try:
        model.db.session.add_all(reports)
        model.db.session.commit()
    except SQLAlchemyError as se:
      app.logger.error(f"{se}")
      model.db.session.rollback()
      return False 
    return True


def delete(report: model.Report, /) -> bool:
    if report is None:
        return False
    
    try:
        model.db.session.delete(report)
        model.db.session.commit()
    except SQLAlchemyError as se:
      app.logger.error(f"{se}")
      model.db.session.rollback()
      return False 
    return True


def delete_all(reports: list[model.Report], /) -> bool:
    if reports is None or not reports:
        return False
    
    try:
        for report in reports:
            try:
                model.db.session.delete(report)
            except SQLAlchemyError as se:
                app.logger.error(f"{se}")
                model.db.session.rollback()
        model.db.session.commit()
    except SQLAlchemyError as se:
      app.logger.error(f"{se}")
      model.db.session.rollback()
      return False 
    return True


def find_report_by_id(id: int, /) -> model.Report | None:
    return model.db.session.scalar(
        sqlalchemy.select(model.Report).filter(model.Report.id == id)
    )


def find_report_by_id_and_company(
    id: int, company: misc.Company, /
) -> model.Report | None:
    return model.db.session.scalar(
        sqlalchemy.select(model.Report)
        .filter(model.Report.id == id)
        .filter(model.Report.company == company.name)
    )


def find_report_by_date_and_company(
    date: datetime.date, company: misc.Company, /
) -> model.Report | None:
    return model.db.session.scalar(
        sqlalchemy.select(model.Report)
        .filter(model.Report.date == date)
        .filter(model.Report.company == company.name)
    )


# empty reports will be hidden, however they'll still persist!
# TODO: find a way to bulk delete all empty reports without interfering with an ongoing transaction 
def find_all_reports_by_company(
    company: misc.Company, order: order_attr.Order, /
) -> list[model.Report]:
    return model.db.session.scalars(
        sqlalchemy.select(model.Report)
        .filter(model.Report.company == company.name)
        .filter(model.Report.presence.any())
        .order_by(
            sqlalchemy.asc(model.Report.date)
            if order == order_attr.Order.ASC
            else sqlalchemy.desc(model.Report.date)
        )
    ).all()


def delete_all_empty_reports_by_company(company: misc.Company) -> None:
    empty_reports = model.db.session.scalars(
        sqlalchemy.select(model.Report)
        .filter(model.Report.company == company.name)
        .filter(model.Report.presence)
        .order_by(model.Report.id.asc)
    ).all()
    
    delete_all(empty_reports)


def find_all_reports() -> list[model.Report]:
    return model.db.session.scalars(sqlalchemy.select(model.Report)).all()