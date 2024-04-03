from enum import Enum
from typing import Self


class Permission():
    def __init__(self: Self, level: int, name: str) -> None:
        self.level = level
        self.name = name
    
    def __repr__(self: Self) -> str:
        return f"Permission(level: {self.level}, name: {self.name})"

class Role(Enum):
    USER = Permission(2, "פקיד.ה")
    MANAGER = Permission(1, "שליש.ה")
    ADMIN = Permission(0, "מנהל.ת")

    @staticmethod
    def is_valid(role_name: str, /) -> bool:
        return role_name in Role._member_names_
    
    @staticmethod
    def get_value(role_name: str) -> str | None:
        if not Role.is_valid(role_name):
            return None
        return Role[role_name].value.name
    
    @staticmethod
    def get_level(role_name: str) -> int | None:
        if not Role.is_valid(role_name):
            return None
        return Role[role_name].value.level
    
    @staticmethod
    def get_name(value_str: str) -> str | None:
        permissions = {member.value.name : name for name, member in Role._member_map_.items()}
        return permissions.get(value_str, None)


class Company(Enum):
    A = "א"
    B = "ב"
    C = "ג"
    SUPPORT = "מסייעת"
    HEADQUARTERS = "מפקדה"

    @staticmethod
    def is_valid(company: str, /) -> bool:
        return company in Company._member_names_


class Platoon(Enum):
    UNCATEGORIZED = "לא משוייך"
    _1 = "1"
    _2 = "2"
    _3 = "3"
    _4 = "4"
    _5 = "5"
    _6 = "6"
    _7 = "7"
    _8 = "8"
    _9 = "9"

    @staticmethod
    def is_valid(platoon: str, /) -> bool:
        return platoon in Platoon._member_names_


class Active(Enum):
    ACTIVE = "פעיל.ה"
    INACTIVE = "לא פעיל.ה"

    @staticmethod
    def is_valid(active: str, /) -> bool:
        return active in Active._member_names_


class Presence(Enum):
    PRESENT = "נמצא.ת"
    NOT_PRESENT = "לא נמצא.ת"

    @staticmethod
    def is_valid(presence: str, /) -> bool:
        return presence in Presence._member_names_
