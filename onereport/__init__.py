import os
import sys
from typing import Any
import flask

def create_app(test_config: dict[str, Any] = None) -> flask.Flask:
  app = flask.Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(SECRET_KEY = "dev", DATABASE = os.path.join(app.instance_path, "onereport.sqlite"))
  
  if not test_config:
    app.config.from_pyfile("config/config.py", silent=True)
  else:
    app.config.from_mapping(test_config)
    
  try:
    os.makedirs(app.instance_path)
  except OSError as os_err:
    print(f"error creating directory {app.instance_path}\n reason: {os_err.strerror}", file=sys.stderr)
    
  # import controller  # noqa: F401
  @app.route("/hello")
  def hello() -> str:
    return "hello, world!"
  
  return app