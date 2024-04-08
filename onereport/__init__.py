import json
import flask
from onereport.data import model, misc
import dotenv
import logging
import logging.config
import os
from onereport.config import Config

# TODO (for prod):
# https://developers.google.com/identity/protocols/oauth2/web-server#uri-validation
# Hosts cannot be raw IP addresses. Localhost IP addresses are exempted from this rule.
# Redirect URIs must use the HTTPS scheme, not plain HTTP



def create_logger(logger_config: str="logger.json", /) -> None:
    with open(logger_config, "r") as file_config:
        config = json.load(file_config)
    logging.config.dictConfig(config)
    

def create_app(config: Config = Config, /) -> flask.Flask:
    # since its a relative path - a better solution should be in place
    if not dotenv.load_dotenv("resources/.env"):
        logging.error("failed to load environment variables")
        exit(1)
    
    create_logger(os.environ.get("LOGGING_CONFIG"))
    
    app = flask.Flask(__name__)
    app.config.from_object(config)

    @app.template_filter()
    def generate_urlstr(role_name: str, urlstr: str) -> str:
        return f"{role_name.lower()}s.{urlstr}"


    @app.template_filter()
    def has_permission(role_name: str) -> bool:
        if not misc.Role.is_valid(role_name):
            return False
        return misc.Role.get_level(role_name) <= misc.Role.get_level(misc.Role.MANAGER.name)


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


    model.db.init_app(app=app)
    model.login_manager.init_app(app=app)


    from onereport.controller.common import common      # noqa: F401
    from onereport.controller.users import users        # noqa: F401
    from onereport.controller.auth import auth          # noqa: F401
    from onereport.controller.managers import managers  # noqa: F401
    from onereport.controller.admins import admins      # noqa: F401
    
    app.register_blueprint(common)
    app.register_blueprint(users)
    app.register_blueprint(auth)
    app.register_blueprint(managers)
    app.register_blueprint(admins)
    
    return app
