from typing import Set
# from personnel_entity import Personnel
import model
import sqlalchemy.orm as orm
import sqlalchemy.types as types
import datetime

class Date(model.db.Model):
  id: orm.Mapped[types.DATE] = orm.mapped_column(primary_key=True, default=datetime.date)
  
  present: orm.Mapped[Set["Personnel"]] = orm.relationship(secondary=model.personal_date_table, back_populates="dates_present")
