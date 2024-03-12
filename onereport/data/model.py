import flask_sqlalchemy
import sqlalchemy.orm as orm
import sqlalchemy

class Base(orm.DeclarativeBase, orm.MappedAsDataclass):
  pass

db = flask_sqlalchemy.SQLAlchemy(model_class=Base)

personal_date_table = sqlalchemy.Table(
  "personnel_date",
  Base.metadata,
  sqlalchemy.Column("date_id", sqlalchemy.ForeignKey("date.id"), primary_key=True),
  sqlalchemy.Column("personnel_id", sqlalchemy.ForeignKey("personnel.id"), primary_key=True),
)