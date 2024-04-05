import json
import logging.config
import flask
from onereport.data import model, misc
import dotenv
import logging
import os

# TODO (for prod):
# https://developers.google.com/identity/protocols/oauth2/web-server#uri-validation
# Hosts cannot be raw IP addresses. Localhost IP addresses are exempted from this rule.
# Redirect URIs must use the HTTPS scheme, not plain HTTP

# since its a relative path - a better solution should be in place
if not dotenv.load_dotenv(dotenv_path="resources/.env"):   
    logging.error("failed to load environment variables")
    exit(1)

with open(os.environ.get("LOGGING_CONFIG"), "r") as file_config:
    config = json.load(file_config)
logging.config.dictConfig(config)

app = flask.Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", None)
if app.config["SECRET_KEY"] is None:
    app.logger.error("failed to load in secret_key")
    exit(1)
    
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI", None)
if app.config["SQLALCHEMY_DATABASE_URI"] is None:
    app.logger.error("failed to load in db uri")
    exit(1)
    
app.config["OAUTH2_PROVIDERS"] = {
    # Google OAuth 2.0 documentation:
    # https://developers.google.com/identity/protocols/oauth2/web-server#httprest
    "google": {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo": {
            "url": "https://www.googleapis.com/oauth2/v3/userinfo",
            "email": lambda json: json["email"],
        },
        "scopes": ["https://www.googleapis.com/auth/userinfo.email"],
    }
}

app.config["PHONE"] = os.environ.get("PHONE", None)
app.config["EMAIL"] = os.environ.get("EMAIL", None)

@app.template_filter()
def generate_urlstr(role_name: str, urlstr: str) -> str:
    if misc.Role[role_name] == misc.Role.USER:
        return f"u_{urlstr}"

    if misc.Role[role_name] == misc.Role.MANAGER:
        return f"m_{urlstr}"

    return f"a_{urlstr}"


@app.template_filter()
def has_permission(role_name: str) -> bool:
    if not misc.Role.is_valid(role_name):
        return False
    return misc.Role.get_level(role_name) <= misc.Role.get_level(misc.Role.MANAGER.name)


@app.template_filter()
def checked(present: bool) -> str:
    return "checked" if present else ""


@app.template_filter()
def is_active(active: bool) -> str:
    return "checked" if active else ""

@app.template_filter()
def get_company_name_by_value(company_value: str) -> str:
    return misc.Company(company_value).name

model.db.init_app(app=app)
model.login_manager.init_app(app=app)

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


def register_personnel(personnel: model.Personnel) -> None:
    if personnel is None:
        raise ValueError("personnel must not be None")

    with app.app_context():
        model.db.session.add(personnel)
        model.db.session.commit()

from onereport.endpoints import common      # noqa: E402, F401
from onereport.endpoints import users       # noqa: E402, F401
from onereport.endpoints import auth        # noqa: E402, F401
from onereport.endpoints import managers    # noqa: E402, F401
from onereport.endpoints import admins      # noqa: E402, F401
