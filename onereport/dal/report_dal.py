from flask_sqlalchemy.pagination import Pagination
from flask import current_app
from onereport.dal import Order
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
        current_app.logger.error(f"{se}")
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
        current_app.logger.error(f"{se}")
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
        current_app.logger.error(f"{se}")
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
        current_app.logger.error(f"{se}")
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
                current_app.logger.error(f"{se}")
                model.db.session.rollback()
        model.db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        model.db.session.rollback()
        return False
    return True


def find_report_by_id(id: int, /) -> model.Report | None:
    return model.db.session.scalar(
        sqlalchemy.select(model.Report).filter(model.Report.id == id)
    )


def find_all_reports_by_date(date: datetime.date, /) -> list[model.Report]:
    return model.db.session.scalars(
        sqlalchemy.select(model.Report)
        .filter(model.Report.date == date)
        .filter(model.Report.presence.any())
    ).all()


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
    company: misc.Company, order: Order, page=1, per_page=20, /
) -> Pagination:
    return model.db.paginate(
        sqlalchemy.select(model.Report)
        .filter(model.Report.company == company.name)
        .filter(model.Report.presence.any())
        .order_by(
            sqlalchemy.asc(model.Report.date)
            if order == Order.ASC
            else sqlalchemy.desc(model.Report.date)
        ),
        page=page,
        per_page=per_page,
    )


def delete_all_empty_reports_by_company(company: misc.Company) -> None:
    empty_reports = model.db.session.scalars(
        sqlalchemy.select(model.Report)
        .filter(model.Report.company == company.name)
        .filter(model.Report.presence)
        .order_by(model.Report.id.asc)
    ).all()

    delete_all(empty_reports)


def find_all_distinct_reports(
    order: Order, page: int = 1, per_page: int = 20, /
) -> Pagination:
    return model.db.paginate(
        sqlalchemy.select(model.Report)
        .filter(model.Report.presence.any())
        .distinct(model.Report.date)  # only works for postgres!
        .order_by(
            sqlalchemy.asc(model.Report.date)
            if order == Order.ASC
            else sqlalchemy.desc(model.Report.date)
        ),
        page=page,
        per_page=per_page,
    )


def find_all_reports() -> list[model.Report]:
    return model.db.session.scalars(sqlalchemy.select(model.Report)).all()
