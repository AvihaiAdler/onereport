from typing import List, Tuple

from onereport.dal import order_attr
from onereport.data import model
from onereport.data import misc
import sqlalchemy


def save(personnel: model.Personnel, /) -> bool:
    if personnel is None:
        return False
    model.db.session.add(personnel)
    model.db.session.commit()
    return True


def update(personnel: model.Personnel, /) -> bool:
    if personnel is None:
        return False
    model.db.session.commit()
    return True

def save_all(personnel: list[model.Personnel], /) -> bool:
    if personnel is None or not personnel:
        return False
    model.db.session.add_all(personnel)
    model.db.session.commit()
    return True


def delete(personnel: model.Personnel, /) -> bool:
    if personnel is None:
        return False
    model.db.session.delete(personnel)
    model.db.session.commit()
    return True


def delete_all(personnel: list[model.Personnel], /) -> bool:
    if personnel is None or not personnel:
        return False
    for p in personnel:
        model.db.session.delete(p)
    model.db.session.commit()
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
    order_by: order_attr.PersonnelOrderBy, order: order_attr.Order, /
) -> sqlalchemy.Select[Tuple]:
    return (
        sqlalchemy.select(model.Personnel).order_by(
            sqlalchemy.asc(order_by.name.lower())
        )
        if order == order_attr.Order.ASC
        else sqlalchemy.select(model.Personnel).order_by(
            sqlalchemy.desc(order_by.name.lower())
        )
    )


def find_all_active_personnel(
    order_by: order_attr.PersonnelOrderBy, order: order_attr.Order, /
) -> List[model.Personnel]:
    return model.db.session.scalars(
        construct_statement(order_by, order).filter(model.Personnel.active)
    ).all()


def find_all_active_personnel_by_company(
    company: misc.Company,
    order_by: order_attr.PersonnelOrderBy,
    order: order_attr.Order,
    /,
) -> List[model.Personnel]:
    return model.db.session.scalars(
        construct_statement(order_by, order)
        .filter(model.Personnel.active)
        .filter(model.Personnel.company == company.name)
    ).all()


def find_all_personnel(
    order_by: order_attr.PersonnelOrderBy, order: order_attr.Order, /
) -> List[model.Personnel]:
    return model.db.session.scalars(construct_statement(order_by, order)).all()
