from onereport.data import model
from onereport.data import misc
from onereport.dal import order_attr
import sqlalchemy

def get_users_by_name(username: str, /) -> model.User | None:
  return model.db.session.scalars(sqlalchemy.select(model.User).filter(model.User.username == username)).all()

def get_user_by_email(email: str, /) -> model.User | None:
  return model.db.session.scalar(sqlalchemy.select(model.User).filter(model.User.email == email))

def construct_statement(order_by: order_attr.UserOrderBy, order: order_attr.Order, /) -> sqlalchemy.Select[tuple]:
  return sqlalchemy.select(model.User).order_by(sqlalchemy.asc(order_by.value)) if order == order_attr.Order.ASC else sqlalchemy.select(model.User).order_by(sqlalchemy.desc(order_by.value))

def get_all_active_users(order_by: order_attr.UserOrderBy, order: order_attr.Order, /) -> list[model.User]:
  statement = construct_statement(order_by, order)
  
  return model.db.session.scalars(statement.filter(model.User.active).filter(model.User.role != misc.Role.ADMIN)).all()

def get_all_users(order_by: order_attr.UserOrderBy, order: order_attr.Order, /) -> list[model.User]:
  statement = construct_statement(order_by, order)
  
  return model.db.session.scalars(statement).all()