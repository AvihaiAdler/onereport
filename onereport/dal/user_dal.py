from typing import List, Tuple
from flask import current_app
from onereport.data import model
from onereport.data import misc
from onereport.dal import UserOrderBy, Order
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError


def save(user: model.User, /) -> bool:
    if user is None:
        return False

    try:
        model.db.session.add(user)
        model.db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        model.db.session.rollback()
        return False
    return True


def update(original: model.User, new: model.User, /) -> bool:
    if original is None or new is None:
        return False

    try:
        original.update_user(new)
        model.db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        model.db.session.rollback()
        return False
    return True


def save_all(users: list[model.User], /) -> bool:
    if users is None or not users:
        return False

    try:
        model.db.session.add_all(users)
        model.db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        model.db.session.rollback()
        return False
    return True


def delete(user: model.User, /) -> bool:
    if user is None:
        return False

    try:
        model.db.session.delete(user)
        model.db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        model.db.session.rollback()
        return False
    return True


def delete_all(users: list[model.User], /) -> bool:
    if users is None or not users:
        return False

    try:
        for user in users:
            try:
                model.db.session.delete(user)
            except SQLAlchemyError as se:
                current_app.logger.error(f"{se}")
                model.db.session.rollback()
        model.db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        model.db.session.rollback()
        return False
    return True


def find_users_by_first_name(first_name: str, /) -> model.User | None:
    return model.db.session.scalars(
        sqlalchemy.select(model.User).filter(model.User.first_name == first_name)
    ).all()


def find_users_by_last_name(last_name: str, /) -> model.User | None:
    return model.db.session.scalars(
        sqlalchemy.select(model.User).filter(model.User.last_name == last_name)
    ).all()


def find_user_by_email(email: str, /) -> model.User | None:
    return model.db.session.scalar(
        sqlalchemy.select(model.User).filter(model.User.email == email)
    )


def construct_statement(
    order_by: UserOrderBy, order: Order, /
) -> sqlalchemy.Select[Tuple]:
    return (
        sqlalchemy.select(model.User).order_by(sqlalchemy.asc(order_by.name.lower()))
        if order == Order.ASC
        else sqlalchemy.select(model.User).order_by(
            sqlalchemy.desc(order_by.name.lower())
        )
    )


def find_all_active_users(order_by: UserOrderBy, order: Order, /) -> List[model.User]:
    statement = construct_statement(order_by, order)

    return model.db.session.scalars(
        statement.filter(model.User.active).filter(
            model.User.role != misc.Role.ADMIN.name
        )
    ).all()


def find_all_users(order_by: UserOrderBy, order: Order, /) -> List[model.User]:
    statement = construct_statement(order_by, order)

    return model.db.session.scalars(statement).all()
