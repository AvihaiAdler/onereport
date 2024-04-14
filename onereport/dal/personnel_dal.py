import datetime
from typing import List, Tuple
from flask import current_app
from onereport.dal import PersonnelOrderBy, Order
from onereport.data import model
from onereport.data import misc
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError


def save(personnel: model.Personnel, /) -> bool:
    if personnel is None:
        return False

    try:
        model.db.session.add(personnel)
        model.db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        model.db.session.rollback()
        return False
    return True


def update(original: model.Personnel, new: model.Personnel, /) -> bool:
    if original is None or new is None:
        return False

    try:
        original.update_personnel(new)
        model.db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        model.db.session.rollback()
        return False
    return True


def save_all(personnel: list[model.Personnel], /) -> bool:
    if personnel is None or not personnel:
        return False

    try:
        model.db.session.add_all(personnel)
        model.db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        model.db.session.rollback()
        return False
    return True


def delete(personnel: model.Personnel, /) -> bool:
    if personnel is None:
        return False

    try:
        model.db.session.delete(personnel)
        model.db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        model.db.session.rollback()
        return False
    return True


def delete_all(personnel: list[model.Personnel], /) -> bool:
    if personnel is None or not personnel:
        return False

    try:
        for p in personnel:
            try:
                model.db.session.delete(p)
            except SQLAlchemyError as se:
                current_app.logger.error(f"{se}")
                model.db.session.rollback()
        model.db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        model.db.session.rollback()
        return False
    return True


def find_personnel_by_id(id: str, /) -> model.Personnel | None:
    return model.db.session.scalar(
        sqlalchemy.select(model.Personnel).filter(model.Personnel.id == id)
    )


def find_personnel_by_first_name(first_name: str, /) -> model.Personnel | None:
    return model.db.session.scalar(
        sqlalchemy.select(model.Personnel).filter(
            model.Personnel.first_name == first_name
        )
    )


def find_personnel_by_last_name(last_name: str, /) -> model.Personnel | None:
    return model.db.session.scalar(
        sqlalchemy.select(model.Personnel).filter(
            model.Personnel.last_name == last_name
        )
    )


def construct_statement(
    order_by: PersonnelOrderBy, order: Order, /
) -> sqlalchemy.Select[Tuple]:
    return (
        sqlalchemy.select(model.Personnel).order_by(
            sqlalchemy.asc(order_by.name.lower())
        )
        if order == Order.ASC
        else sqlalchemy.select(model.Personnel).order_by(
            sqlalchemy.desc(order_by.name.lower())
        )
    )


def find_all_active_personnel(
    order_by: PersonnelOrderBy, order: Order, /
) -> List[model.Personnel]:
    return model.db.session.scalars(
        construct_statement(order_by, order).filter(model.Personnel.active)
    ).all()


def find_all_active_personnel_by_company(
    company: misc.Company,
    order_by: PersonnelOrderBy,
    order: Order,
    /,
) -> List[model.Personnel]:
    return model.db.session.scalars(
        construct_statement(order_by, order)
        .filter(model.Personnel.active)
        .filter(model.Personnel.company == company.name)
    ).all()


def find_all_personnel(
    order_by: PersonnelOrderBy, order: Order, /
) -> List[model.Personnel]:
    return model.db.session.scalars(construct_statement(order_by, order)).all()


def find_all_personnel_by_company(
    company: misc.Company,
    order_by: PersonnelOrderBy,
    order: Order,
    /,
) -> List[model.Personnel]:
    return model.db.session.scalars(
        construct_statement(order_by, order).filter(model.User.company == company.name)
    ).all()


def find_all_personnel_by_company_dated_before(
    company: misc.Company,
    date: datetime.date,
    order_by: PersonnelOrderBy,
    order: Order,
    /,
) -> list[model.Personnel]:
    return model.db.session.scalars(
        construct_statement(order_by, order)
        .filter(model.Personnel.company == company.name)
        .filter(model.Personnel.date_added <= date)
    ).all()


def find_all_personnel_by_company_active_in(
    company: misc.Company,
    date: datetime.date,
    order_by: PersonnelOrderBy,
    order: Order,
    /,
) -> list[model.Personnel]:
    return model.db.session.scalars(
        construct_statement(order_by, order)
        .filter(model.Personnel.company == company.name)
        .filter(model.Personnel.date_added <= date)
        .filter(
            sqlalchemy.or_(
                model.Personnel.date_removed == None,
                model.Personnel.date_removed >= date,
            )
        )
    ).all()


def find_all_personnel_dated_before(
    date: datetime.date, order_by: PersonnelOrderBy, order: Order, /
) -> list[model.Personnel]:
    return model.db.session.scalars(
        construct_statement(order_by, order).filter(model.Personnel.date_added <= date)
    ).all()


def find_all_personnel_active_in(
    date: datetime.date,
    order_by: PersonnelOrderBy,
    order: Order,
    /,
) -> list[model.Personnel]:
    return model.db.session.scalars(
        construct_statement(order_by, order)
        .filter(model.Personnel.date_added <= date)
        .filter(
            sqlalchemy.or_(
                model.Personnel.date_removed == None,
                model.Personnel.date_removed >= date,
            )
        )
    ).all()
