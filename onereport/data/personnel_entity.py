from typing import Set
# from date_entity import Date
import model
import sqlalchemy.orm as orm 

class Personnel(model.db.Model):
  id: orm.Mapped[str] = orm.mapped_column(primary_key=True)
  first_name: orm.Mapped[str]
  last_name: orm.Mapped[str]
  company: orm.Mapped[str]
  platoon: orm.Mapped[str]
  active: orm.Mapped[bool] = orm.mapped_column(default=True)
  
  dates_present: orm.mapped_column[Set["Date"]] = orm.relationship(secondary=model.personal_date_table, back_populates="present")
