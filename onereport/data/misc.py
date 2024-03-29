from enum import Enum


class Role(Enum):
    USER = "פקיד"
    MANAGER = "שליש"
    ADMIN = "מנהל"

    @staticmethod
    def is_valid(role: str, /) -> bool:
        return role in Role._member_names_


class Company(Enum):
    A = "פלוגה א"
    B = "פלוגה ב"
    C = "פלוגה ג"
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
    ACTIVE = "פעיל"
    INACTIVE = "לא פעיל"

    @staticmethod
    def is_valid(active: str, /) -> bool:
        return active in Active._member_names_


class Presence(Enum):
    PRESENT = "נמצא"
    NOT_PRESENT = "לא נמצא"

    @staticmethod
    def is_valid(presence: str, /) -> bool:
        return presence in Presence._member_names_
