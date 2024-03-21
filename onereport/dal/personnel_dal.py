from onereport.dal import order_attr
from onereport.data import model
from onereport.data import misc
import sqlalchemy

def get_personnel_by_id(id: str) -> model.Personnel | None:
  return model.db.session.scalar(sqlalchemy.select(model.Personnel).filter(model.Personnel.id == id))

def get_personnel_by_first_name(first_name: str) -> model.Personnel | None:
  return model.db.session.scalar(sqlalchemy.select(model.Personnel).filter(model.Personnel.first_name == first_name))

def get_personnel_by_last_name(last_name: str) -> model.Personnel | None:
  return model.db.session.scalar(sqlalchemy.select(model.Personnel).filter(model.Personnel.last_name == last_name))

def construct_statement(order_by: order_attr.PersonnelOrderBy, order: order_attr.Order, /) -> sqlalchemy.Select[tuple]:
  return sqlalchemy.select(model.Personnel).order_by(sqlalchemy.asc(order_by.name.lower())) if order == order_attr.Order.ASC else sqlalchemy.select(model.Personnel).order_by(sqlalchemy.desc(order_by.name.lower()))

def get_all_active_personnel(order_by: order_attr.PersonnelOrderBy, order: order_attr.Order, /) -> list[model.Personnel]:
  return model.db.session.scalars(construct_statement(order_by, order).filter(model.Personnel.active)).all()

def get_all_active_personnel_by_company(company: misc.Company, order_by: order_attr.PersonnelOrderBy, order: order_attr.Order, /) -> list[model.Personnel]:
  return model.db.session.scalars(construct_statement(order_by, order).filter(model.Personnel.active).filter(model.Personnel.company == company.name)).all()

def get_all_personnel(order_by: order_attr.PersonnelOrderBy, order: order_attr.Order, /) -> list[model.Personnel]:
  return model.db.session.scalars(construct_statement(order_by, order)).all()