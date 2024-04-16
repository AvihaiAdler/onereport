import datetime
from typing import List, Tuple
from flask import current_app
from onereport.dal import PersonnelOrderBy, Order
from onereport.data import db, Personnel, User
from onereport.data import misc
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError


def save(personnel: Personnel, /) -> bool:
    if personnel is None:
        return False

    try:
        db.session.add(personnel)
        db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        db.session.rollback()
        return False
    return True


def update(original: Personnel, new: Personnel, /) -> bool:
    if original is None or new is None:
        return False

    try:
        original.update_personnel(new)
        db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        db.session.rollback()
        return False
    return True


def save_all(personnel: list[Personnel], /) -> bool:
    if personnel is None or not personnel:
        return False

    try:
        db.session.add_all(personnel)
        db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        db.session.rollback()
        return False
    return True


def delete(personnel: Personnel, /) -> bool:
    if personnel is None:
        return False

    try:
        db.session.delete(personnel)
        db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        db.session.rollback()
        return False
    return True


def delete_all(personnel: list[Personnel], /) -> bool:
    if personnel is None or not personnel:
        return False

    try:
        for p in personnel:
            try:
                db.session.delete(p)
            except SQLAlchemyError as se:
                current_app.logger.error(f"{se}")
                db.session.rollback()
        db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        db.session.rollback()
        return False
    return True


def find_personnel_by_id(id: str, /) -> Personnel | None:
    return db.session.scalar(
        sqlalchemy.select(Personnel).filter(Personnel.id == id)
    )


def find_personnel_by_first_name(first_name: str, /) -> Personnel | None:
    return db.session.scalar(
        sqlalchemy.select(Personnel).filter(
            Personnel.first_name == first_name
        )
    )


def find_personnel_by_last_name(last_name: str, /) -> Personnel | None:
    return db.session.scalar(
        sqlalchemy.select(Personnel).filter(
            Personnel.last_name == last_name
        )
    )


def construct_statement(
    order_by: PersonnelOrderBy, order: Order, /
) -> sqlalchemy.Select[Tuple]:
    return (
        sqlalchemy.select(Personnel).order_by(
            sqlalchemy.asc(order_by.name.lower())
        )
        if order == Order.ASC
        else sqlalchemy.select(Personnel).order_by(
            sqlalchemy.desc(order_by.name.lower())
        )
    )


def find_all_active_personnel(
    order_by: PersonnelOrderBy, order: Order, /
) -> List[Personnel]:
    return db.session.scalars(
        construct_statement(order_by, order).filter(Personnel.active)
    ).all()


def find_all_active_personnel_by_company(
    company: misc.Company,
    order_by: PersonnelOrderBy,
    order: Order,
    /,
) -> List[Personnel]:
    return db.session.scalars(
        construct_statement(order_by, order)
        .filter(Personnel.active)
        .filter(Personnel.company == company.name)
    ).all()


def find_all_personnel(
    order_by: PersonnelOrderBy, order: Order, /
) -> List[Personnel]:
    return db.session.scalars(construct_statement(order_by, order)).all()


def find_all_personnel_by_company(
    company: misc.Company,
    order_by: PersonnelOrderBy,
    order: Order,
    /,
) -> List[Personnel]:
    return db.session.scalars(
        construct_statement(order_by, order).filter(User.company == company.name)
    ).all()


def find_all_personnel_by_company_dated_before(
    company: misc.Company,
    date: datetime.date,
    order_by: PersonnelOrderBy,
    order: Order,
    /,
) -> list[Personnel]:
    return db.session.scalars(
        construct_statement(order_by, order)
        .filter(Personnel.company == company.name)
        .filter(Personnel.date_added <= date)
    ).all()


def find_all_personnel_by_company_active_in(
    company: misc.Company,
    date: datetime.date,
    order_by: PersonnelOrderBy,
    order: Order,
    /,
) -> list[Personnel]:
    return db.session.scalars(
        construct_statement(order_by, order)
        .filter(Personnel.company == company.name)
        .filter(Personnel.date_added <= date)
        .filter(
            sqlalchemy.or_(
                Personnel.date_removed == None,  # noqa: E711
                Personnel.date_removed >= date,
            )
        )
    ).all()


def find_all_personnel_dated_before(
    date: datetime.date, order_by: PersonnelOrderBy, order: Order, /
) -> list[Personnel]:
    return db.session.scalars(
        construct_statement(order_by, order).filter(Personnel.date_added <= date)
    ).all()


def find_all_personnel_active_in(
    date: datetime.date,
    order_by: PersonnelOrderBy,
    order: Order,
    /,
) -> list[Personnel]:
    return db.session.scalars(
        construct_statement(order_by, order)
        .filter(Personnel.date_added <= date)
        .filter(
            sqlalchemy.or_(
                Personnel.date_removed == None,  # noqa: E711
                Personnel.date_removed >= date,
            )
        )
    ).all()
