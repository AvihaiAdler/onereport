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
  first_name: orm.Mapped[str]
  last_name: orm.Mapped[str]
  role: orm.Mapped[str]
  company: orm.Mapped[str]
  active: orm.Mapped[bool]= orm.mapped_column(default=True)
  
  def __init__(self: Self, email: str, first_name: str, last_name: str, role: str, company: str, /) -> None:
    super().__init__(email=email, first_name=first_name, last_name=last_name, role=role, company=company)
    
  def update(self: Self, other: Self) -> None:
    self.first_name, self.last_name = other.first_name, other.last_name
  
  def __repr__(self: Self) -> str:
    return f"User(email: {self.email}, name: {' '.join((self.first_name, self.last_name))}, role: {self.role}, company: {self.company}, active: {self.active})"
  
  def get_id(self: Self) -> str:
    return self.email

@login_manager.user_loader
def load_user(email: str) -> User:
  return db.session.get(User, email)

personnel_report_rel = sqlalchemy.Table(
  "personnel_report_rel",
  Base.metadata,
  sqlalchemy.Column("report_id", sqlalchemy.ForeignKey("report.id"), primary_key=True),
  sqlalchemy.Column("personnel_id", sqlalchemy.ForeignKey("personnel.id"), primary_key=True),
)

class Personnel(db.Model):
  id: orm.Mapped[str] = orm.mapped_column(primary_key=True)
  first_name: orm.Mapped[str]
  last_name: orm.Mapped[str]
  company: orm.Mapped[str]
  platoon: orm.Mapped[str]
  active: orm.Mapped[bool] = orm.mapped_column(default=True)
  
  dates_present: orm.Mapped[Set["Report"]] = orm.relationship(secondary=personnel_report_rel, back_populates="presence", lazy=True)
  
  def __init__(self: Self, id: str, first_name: str, last_name: str, company: str, platoon: str, /) -> None:
    super().__init__(id=id, first_name=first_name, last_name=last_name, company=company, platoon=platoon)
  
  def update(self: Self, other: Self) -> None:
    self.first_name, self.last_name = other.first_name, other.last_name
    self.company = other.company
    self.platoon = other.platoon
    self.active = other.active
  
  def __repr__(self: Self) -> str:
    return f"Personnel(id: {self.id}, full name:{' '.join((self.first_name, self.last_name))}, company: {self.company}, platoon: {self.platoon}, active: {self.active})"
  

class Report(db.Model):
  id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
  date: orm.Mapped[datetime.date] = orm.mapped_column(default=datetime.date.today)
  company: orm.Mapped[str]
  
  presence: orm.Mapped[Set["Personnel"]] = orm.relationship(secondary=personnel_report_rel, back_populates="dates_present", lazy=True)

  def __init__(self: Self, company: str, /) -> None:
    super().__init__(company=company)

  def __repr__(self: Self) -> str:
    return f"Report(date: {self.date.day}/{self.date.month}/{self.date.year}, company: {self.company})"

