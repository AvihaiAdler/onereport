import flask
from onereport.data import model, misc
import dotenv
import logging
import os

# TODO (for prod): 
# https://developers.google.com/identity/protocols/oauth2/web-server#uri-validation
# Hosts cannot be raw IP addresses. Localhost IP addresses are exempted from this rule.
# Redirect URIs must use the HTTPS scheme, not plain HTTP

if not dotenv.load_dotenv():
    logging.error("failed to load environment variables")
    exit(1)
    
app = flask.Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config["OAUTH2_PROVIDERS"] = {
    # Google OAuth 2.0 documentation:
    # https://developers.google.com/identity/protocols/oauth2/web-server#httprest
    "google": {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        "authorize_url": "https://accounts.google.com/o/oauth2/auth",
        "token_url": "https://accounts.google.com/o/oauth2/token",
        "userinfo": {
            "url": "https://www.googleapis.com/oauth2/v3/userinfo",
            "email": lambda json: json["email"],
        },
        "scopes": ["https://www.googleapis.com/auth/userinfo.email"],
    }
}

@app.template_filter()
def check_user(role: str) -> bool:
  return misc.Role[role] == misc.Role.USER

@app.template_filter()
def generate_urlstr(role: str, urlstr: str) -> str:
  if misc.Role[role] == misc.Role.USER:
    return f"u_{urlstr}"
  
  if misc.Role[role] == misc.Role.MANAGER:
    return f"m_{urlstr}"
  
  return f"a_{urlstr}"

@app.template_filter()
def is_not_user(role: str) -> bool:
  return misc.Role[role] != misc.Role.USER

@app.template_filter()
def checked(present: bool) -> str:
  return "checked" if present else ""

model.db.init_app(app=app)
model.login_manager.init_app(app=app)
model.login_manager.login_view = "login"
model.login_manager.login_message_category = "info"

def drop_all() -> None:
  with app.app_context():
    model.db.drop_all()
    
def create_all() -> None:
  with app.app_context():
    model.db.create_all()
    
def register_user(user: model.User) -> None:
  if user is None:
    raise ValueError("user must not be None")
  
  with app.app_context():
    model.db.session.add(user)
    model.db.session.commit()

from onereport.endpoints import users  # noqa: E402, F401
from onereport.endpoints import auth  # noqa: E402, F401
from onereport.endpoints import managers # noqa: E402, F401
from onereport.endpoints import admins # noqa: E402, F401
