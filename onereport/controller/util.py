from onereport.data.misc import Role


def generate_url(role_name: str, func_name: str) -> str:
    if not Role.is_valid(role_name):
        return "common.login"

    return f"{role_name.lower()}s.{func_name}"


def not_permitted(role_name: str, role: Role, /) -> bool:
    if not Role.is_valid(role_name):
        return True
    return Role.get_level(role_name) > role.value.level
