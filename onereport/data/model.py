from typing import Self, Set
import sqlalchemy.orm as orm
from flask_sqlalchemy import SQLAlchemy
import datetime
import sqlalchemy
from flask_login import UserMixin, LoginManager

class Base(orm.DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

login_manager = LoginManager()

class User(db.Model, UserMixin):
  email: orm.Mapped[str] = orm.mapped_column(primary_key=True)
  username: orm.Mapped[str]
  role: orm.Mapped[str]
  company: orm.Mapped[str]
  active: orm.Mapped[bool]= orm.mapped_column(default=True)
  
  def __init__(self, email: str, username: str, role: str, company: str, /) -> None:
    super().__init__(email=email, username=username, role=role, company=company)
  
  def __repr__(self: Self) -> str:
    return f"User(email: {self.email}, username: {self.username}, role: {self.role}, company: {self.company}, active: {self.active})"
  
  def get_id(self: Self) -> str:
    return self.email

@login_manager.user_loader
def load_user(email: str) -> User:
  return db.session.get(User, email)

personnel_date = sqlalchemy.Table(
  "personnel_date",
  Base.metadata,
  sqlalchemy.Column("date_id", sqlalchemy.ForeignKey("date.id"), primary_key=True),
  sqlalchemy.Column("personnel_id", sqlalchemy.ForeignKey("personnel.id"), primary_key=True),
)

class Personnel(db.Model):
  id: orm.Mapped[str] = orm.mapped_column(primary_key=True)
  first_name: orm.Mapped[str]
  last_name: orm.Mapped[str]
  company: orm.Mapped[str]
  platoon: orm.Mapped[str]
  active: orm.Mapped[bool] = orm.mapped_column(default=True)
  
  dates_present: orm.Mapped[Set["Date"]] = orm.relationship(secondary=personnel_date, back_populates="present", lazy=True)
  
  def __init__(self, id: str, first_name: str, last_name: str, company: str, platoon: str, /) -> None:
    super().__init__(id=id, first_name=first_name, last_name=last_name, company=company, platoon=platoon)
  
  def __repr__(self: Self) -> str:
    return f"Personnel(id: {self.id}, full name:{' '.join((self.first_name, self.last_name))}, company: {self.company}, platoon: {self.platoon}, active: {self.active})"
  

class Date(db.Model):
  id: orm.Mapped[datetime.date] = orm.mapped_column(primary_key=True, default=datetime.date.today)
  
  present: orm.Mapped[Set["Personnel"]] = orm.relationship(secondary=personnel_date, back_populates="dates_present", lazy=True)

  def __init__(self) -> None:
    super().__init__()
    
  def get_id(self: Self) -> datetime.date:
    return Self.id

  def __repr__(self: Self) -> str:
    return f"Date({self.id.day}/{self.id.month}/{self.id.year})"

