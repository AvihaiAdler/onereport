from typing import List, Tuple
from flask import current_app
from onereport.data import db, User
from onereport.data import misc
from onereport.dal import UserOrderBy, Order
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError


def save(user: User, /) -> bool:
    if user is None:
        return False

    try:
        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        db.session.rollback()
        return False
    return True


def update(original: User, new: User, /) -> bool:
    if original is None or new is None:
        return False

    try:
        original.update_user(new)
        db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        db.session.rollback()
        return False
    return True


def save_all(users: list[User], /) -> bool:
    if users is None or not users:
        return False

    try:
        db.session.add_all(users)
        db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        db.session.rollback()
        return False
    return True


def delete(user: User, /) -> bool:
    if user is None:
        return False

    try:
        db.session.delete(user)
        db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        db.session.rollback()
        return False
    return True


def delete_all(users: list[User], /) -> bool:
    if users is None or not users:
        return False

    try:
        for user in users:
            try:
                db.session.delete(user)
            except SQLAlchemyError as se:
                current_app.logger.error(f"{se}")
                db.session.rollback()
        db.session.commit()
    except SQLAlchemyError as se:
        current_app.logger.error(f"{se}")
        db.session.rollback()
        return False
    return True


def find_users_by_first_name(first_name: str, /) -> User | None:
    return db.session.scalars(
        sqlalchemy.select(User).filter(User.first_name == first_name)
    ).all()


def find_users_by_last_name(last_name: str, /) -> User | None:
    return db.session.scalars(
        sqlalchemy.select(User).filter(User.last_name == last_name)
    ).all()


def find_user_by_id(id: str, /) -> User | None:
    return db.session.scalar(sqlalchemy.select(User).filter(User.id == id))


def find_user_by_email(email: str, /) -> User | None:
    return db.session.scalar(sqlalchemy.select(User).filter(User.email == email))


def construct_statement(
    order_by: UserOrderBy, order: Order, /
) -> sqlalchemy.Select[Tuple]:
    return (
        sqlalchemy.select(User).order_by(sqlalchemy.asc(order_by.name.lower()))
        if order == Order.ASC
        else sqlalchemy.select(User).order_by(sqlalchemy.desc(order_by.name.lower()))
    )


def find_all_active_users(order_by: UserOrderBy, order: Order, /) -> List[User]:
    statement = construct_statement(order_by, order)

    return db.session.scalars(
        statement.filter(User.active).filter(User.role != misc.Role.ADMIN.name)
    ).all()


def find_all_users(order_by: UserOrderBy, order: Order, /) -> List[User]:
    statement = construct_statement(order_by, order)

    return db.session.scalars(statement).all()
