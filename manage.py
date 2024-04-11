from flask.cli import FlaskGroup
from onereport import create_app

cli = FlaskGroup(create_app=create_app, load_dotenv=True)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
