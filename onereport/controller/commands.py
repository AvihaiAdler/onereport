import json
import click
from onereport.data.model import db, User, Personnel
from onereport.dal import personnel_dal, user_dal
from flask import Blueprint

commands = Blueprint("commands", __name__)


def user_converter(_json: dict[str, str], /) -> User:
    if not _json:
        raise ValueError("User must not be empty")

    return User(
        _json["id"],
        _json["email"],
        _json["first_name"],
        _json["last_name"],
        _json["role"],
        _json["company"],
        _json["platoon"],
    )


def personnel_converter(_json: dict[str, str], /) -> Personnel:
    if not _json:
        raise ValueError("Personnel must not be empty")

    return Personnel(
        _json["id"],
        _json["first_name"],
        _json["last_name"],
        _json["company"],
        _json["platoon"],
    )


def bulk_register_users(users: list[dict[str, str]], /) -> None:
    if users is None:
        return

    users = [user_converter(user) for user in users]
    user_dal.save_all(users)


def bulk_register_personnel(personnel: list[dict[str, str]], /) -> None:
    if personnel is None:
        return

    personnel = [personnel_converter(p) for p in personnel]
    personnel_dal.save_all(personnel)


@commands.cli.command("register_users")
@click.argument("path")
def db_register_users(path: str) -> None:
    with open(path, "r") as f:
        json_dump = json.load(f)

    users = json_dump.get("users", None)
    bulk_register_users(users)

    personnel = json_dump.get("Personnel", None)
    bulk_register_personnel(personnel)


@commands.cli.command("register_user")
@click.argument("user_as_json")
def db_register_user(user_as_json: str) -> None:
    user = json.loads(user_as_json)

    # if the user is invalid - just throw
    user = user_converter(user)
    user_dal.save(user)


@commands.cli.command("register_personnel")
@click.argument("personnel_as_json")
def db_register_personnel(personnel_as_json: str) -> None:
    personnel = json.loads(personnel_as_json)

    # if the personnel is invalid - just throw
    personnel = personnel_converter(personnel)
    personnel_dal.save(personnel)


@commands.cli.command("db_create")
def db_create() -> None:
    db.create_all()
    db.session.commit()


@commands.cli.command("db_destroy")
def db_destroy() -> None:
    db.drop_all()
    db.session.commit()
