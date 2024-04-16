from flask_sqlalchemy.pagination import Pagination
from flask import current_app
from onereport.dal import Order
from onereport.data import db, misc, Report, Personnel, User
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
import datetime


def save(report: Report, /) -> bool:
    if report is None:
        return False

    try:
        db.session.add(report)
        db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        db.session.rollback()
        return False
    return True


def update(report: Report, presence: set[Personnel], user: User=None, /) -> bool:
    if report is None:
        return False

    try:
        report.update(presence, user)
        db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        db.session.rollback()
        return False
    return True


def save_all(reports: list[Report], /) -> bool:
    if reports is None or not reports:
        return False

    try:
        db.session.add_all(reports)
        db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        db.session.rollback()
        return False
    return True


def delete(report: Report, /) -> bool:
    if report is None:
        return False

    try:
        db.session.delete(report)
        db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        db.session.rollback()
        return False
    return True


def delete_all(reports: list[Report], /) -> bool:
    if reports is None or not reports:
        return False

    try:
        for report in reports:
            try:
                db.session.delete(report)
            except SQLAlchemyError as se:
                current_app.logger.error(f"{se}")
                db.session.rollback()
        db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        db.session.rollback()
        return False
    return True


def find_report_by_id(id: int, /) -> Report | None:
    return db.session.scalar(
        sqlalchemy.select(Report).filter(Report.id == id)
    )


def find_all_reports_by_date(date: datetime.date, /) -> list[Report]:
    return db.session.scalars(
        sqlalchemy.select(Report)
        .filter(Report.date == date)
        .filter(Report.presence.any())
    ).all()


def find_report_by_id_and_company(
    id: int, company: misc.Company, /
) -> Report | None:
    return db.session.scalar(
        sqlalchemy.select(Report)
        .filter(Report.id == id)
        .filter(Report.company == company.name)
    )


def find_report_by_date_and_company(
    date: datetime.date, company: misc.Company, /
) -> Report | None:
    return db.session.scalar(
        sqlalchemy.select(Report)
        .filter(Report.date == date)
        .filter(Report.company == company.name)
    )


# empty reports will be hidden, however they'll still persist!
# TODO: find a way to bulk delete all empty reports without interfering with an ongoing transaction
def find_all_reports_by_company(
    company: misc.Company, order: Order, page=1, per_page=20, /
) -> Pagination:
    return db.paginate(
        sqlalchemy.select(Report)
        .filter(Report.company == company.name)
        .filter(Report.presence.any())
        .order_by(
            sqlalchemy.asc(Report.date)
            if order == Order.ASC
            else sqlalchemy.desc(Report.date)
        ),
        page=page,
        per_page=per_page,
    )


def delete_all_empty_reports_by_company(company: misc.Company) -> None:
    empty_reports = db.session.scalars(
        sqlalchemy.select(Report)
        .filter(Report.company == company.name)
        .filter(Report.presence)
        .order_by(Report.id.asc)
    ).all()

    delete_all(empty_reports)


def find_all_distinct_reports(
    order: Order, page: int = 1, per_page: int = 20, /
) -> Pagination:
    return db.paginate(
        sqlalchemy.select(Report)
        .filter(Report.presence.any())
        .distinct(Report.date)  # only works for postgres!
        .order_by(
            sqlalchemy.asc(Report.date)
            if order == Order.ASC
            else sqlalchemy.desc(Report.date)
        ),
        page=page,
        per_page=per_page,
    )


def find_all_reports() -> list[Report]:
    return db.session.scalars(sqlalchemy.select(Report)).all()
