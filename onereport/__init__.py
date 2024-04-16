import os
import json
import flask
import logging
from typing import Any
import logging.config
from pathlib import Path
from onereport.data import db, login_manager, misc
from os.path import dirname, abspath
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix


# https://developers.google.com/identity/protocols/oauth2/web-server#uri-validation
# Hosts cannot be raw IP addresses. Localhost IP addresses are exempted from this rule.
# Redirect URIs must use the HTTPS scheme, not plain HTTP


def create_logger(logger_config: str = "logger.json", /) -> None:
    with open(logger_config, "r") as file_config:
        config = json.load(file_config)

    logging.config.dictConfig(config)


def register_filters(app: flask.Flask, /) -> None:
    @app.template_filter()
    def generate_urlstr(role_name: str, urlstr: str) -> str:
        return f"{role_name.lower()}s.{urlstr}"

    @app.template_filter()
    def has_permission(role_name: str) -> bool:
        if not misc.Role.is_valid(role_name):
            return False
        return misc.Role.get_level(role_name) <= misc.Role.get_level(
            misc.Role.MANAGER.name
        )

    @app.template_filter()
    def is_admin(role_name: str) -> bool:
        if not misc.Role.is_valid(role_name):
            return False
        return misc.Role.get_level(role_name) == misc.Role.get_level(
            misc.Role.ADMIN.name
        )

    @app.template_filter()
    def is_present(present: bool) -> str:
        return "checked" if present else ""

    @app.template_filter()
    def is_active(active: bool) -> str:
        return "checked" if active else ""

    @app.template_filter()
    def get_company_name_by_value(company_value: str) -> str:
        return misc.Company(company_value).name

    @app.template_filter()
    def get_company_value_by_name(company_name: str) -> str:
        return (
            misc.Company[company_name].value
            if misc.Company.is_valid(company_name)
            else "לא תקינה"
        )


def create_app(config: Any = None, /) -> flask.Flask:
    env_file_path = Path(abspath(dirname(__file__))).absolute()
    if not load_dotenv(f"{env_file_path}/.env"):
        logging.error(f"failed to load .env file from {env_file_path}")
        exit(1)

    if config is None:
        from onereport.config import Config
        config = Config()

    create_logger(os.environ.get("LOGGING_CONFIG"))

    app = flask.Flask(__name__)
    app.config.from_object(config)

    db.init_app(app=app)
    login_manager.init_app(app=app)

    from onereport.controller.common import common  # noqa: F401
    from onereport.controller.users import users  # noqa: F401
    from onereport.controller.auth import auth  # noqa: F401
    from onereport.controller.managers import managers  # noqa: F401
    from onereport.controller.admins import admins  # noqa: F401
    from onereport.controller.errors import errors  # noqa: F401
    from onereport.controller.commands import commands  # noqa: F401

    app.register_blueprint(common)
    app.register_blueprint(users)
    app.register_blueprint(auth)
    app.register_blueprint(managers)
    app.register_blueprint(admins)
    app.register_blueprint(errors)
    app.register_blueprint(commands)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    register_filters(app)

    return app
