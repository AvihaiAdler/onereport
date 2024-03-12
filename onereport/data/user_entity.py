import model
import sqlalchemy.orm as orm

class User(model.db.Model):
  email: orm.Mapped[str] = orm.mapped_column(primary_key=True)
  username: orm.Mapped[str]
  role: orm.Mapped[str]
  space: orm.Mapped[str]
  active: orm.Mapped[bool]= orm.mapped_column(default=True)