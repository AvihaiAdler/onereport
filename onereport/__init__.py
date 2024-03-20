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
app.config["SECRET_KEY"] = "f380646b8a62c55a9f1c526f9a62331fdf57f36b2e3165a29b1f92e868e26df14869967414fffe2d808df5e30dc650ef366faac83f36a51886d713b6322571dd"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
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

model.db.init_app(app=app)
model.login_manager.init_app(app=app)
model.login_manager.login_view = "login"
model.login_manager.login_message_category = "info"

# from onereport import endpoints  # noqa: E402, F401
from onereport.endpoints import users  # noqa: E402, F401
from onereport.endpoints import auth  # noqa: E402, F401
from onereport.endpoints import managers # noqa: E402, F401
from onereport.endpoints import admins # noqa: E402, F401

@app.template_filter()
def check_user(role: str) -> bool:
  return misc.Role[role] == misc.Role.USER

@app.template_filter()
def generate_urlstr(role: str, urlstr: str) -> str:
  if misc.Role[role] == misc.Role.USER:
    return f"u_{urlstr}"
  
  if misc.Role[role] == misc.Role.MANAGER:
    return f"m_{urlstr}"
  
  urlstr = "_".join([token for token in urlstr.split("_") if token != "active"])
  return f"a_{urlstr}"