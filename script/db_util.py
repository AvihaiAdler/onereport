import json
import sys
import pathlib

parent_path = pathlib.Path(pathlib.Path(pathlib.Path(__file__).parent.absolute()).parent.absolute())
sys.path.append(parent_path.as_posix()) # https://stackoverflow.com/a/61235118

from onereport import app, drop_all, create_all, register_user, register_personnel
from onereport.data.model import User, Personnel


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

    for user in users:
        user = user_converter(user)
        register_user(user)

        # print(f"The user: {user} registered successfully")


def bulk_register_personnel(personnel: list[dict[str, str]], /) -> None:
    if personnel is None:
        return

    for p in personnel:
        p = personnel_converter(p)
        register_personnel(p)

        # print(f"The personnel: {p} registered successfully")


def main() -> None:
    argv = sys.argv
    if len(argv) < 2:
        print(f"Usage: {argv[0]} path/to/data.json", file=sys.stdout)
        return

    data_file_path = argv[1]

    with app.app_context():
        drop_all()
        create_all()

    json_dump = None
    with open(data_file_path) as fp:
        json_dump = json.load(fp)

    if json_dump is None:
        print(f"failed to load json {data_file_path}", file=sys.stderr)
        return

    users = json_dump.get("Users", None)
    bulk_register_users(users)

    personnel = json_dump.get("Personnel", None)
    bulk_register_personnel(personnel)


if __name__ == "__main__":
    main()
