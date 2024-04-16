import sqlalchemy.orm as orm
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import select

class Base(orm.DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
login_manager.login_view = "common.login"
login_manager.login_message_category = "info"
login_manager.login_message = "אנא התחבר למערכת על מנת להכנס"

from onereport.data.user import User  # noqa: E402

@login_manager.user_loader
def load_user(email: str) -> User | None:
    return db.session.scalar(select(User).filter(User.email == email))