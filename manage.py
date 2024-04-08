import sys
import pathlib

parent_path = pathlib.Path(pathlib.Path(pathlib.Path(__file__).parent.absolute()).parent.absolute())
sys.path.append(parent_path.as_posix()) # https://stackoverflow.com/a/61235118

from flask.cli import FlaskGroup  # noqa: E402
from onereport import app         # noqa: E402

def main() -> None:
  cli = FlaskGroup(app)
  cli()
  
if __name__ == "__main___":
  main()