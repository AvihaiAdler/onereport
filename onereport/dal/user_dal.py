from onereport.data import model
from onereport.data import misc
from onereport.dal import order_attr
import sqlalchemy

def get_users_by_first_name(first_name: str, /) -> model.User | None:
  return model.db.session.scalars(sqlalchemy.select(model.User).filter(model.User.first_name == first_name)).all()

def get_users_by_last_name(last_name: str, /) -> model.User | None:
  return model.db.session.scalars(sqlalchemy.select(model.User).filter(model.User.last_name == last_name)).all()

def get_user_by_email(email: str, /) -> model.User | None:
  return model.db.session.scalar(sqlalchemy.select(model.User).filter(model.User.email == email))

def construct_statement(order_by: order_attr.UserOrderBy, order: order_attr.Order, /) -> sqlalchemy.Select[tuple]:
  return sqlalchemy.select(model.User).order_by(sqlalchemy.asc(order_by.name.lower())) if order == order_attr.Order.ASC else sqlalchemy.select(model.User).order_by(sqlalchemy.desc(order_by.name.lower()))

def get_all_active_users(order_by: order_attr.UserOrderBy, order: order_attr.Order, /) -> list[model.User]:
  statement = construct_statement(order_by, order)
  
  return model.db.session.scalars(statement.filter(model.User.active).filter(model.User.role != misc.Role.ADMIN)).all()

def get_all_users(order_by: order_attr.UserOrderBy, order: order_attr.Order, /) -> list[model.User]:
  statement = construct_statement(order_by, order)
  
  return model.db.session.scalars(statement).all()