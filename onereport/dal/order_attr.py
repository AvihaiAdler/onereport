from enum import Enum


class Order(Enum):
    ASC = "עולה"
    DESC = "יורד"

    @staticmethod
    def is_valid(order: str) -> bool:
        return order in Order._member_names_


class UserOrderBy(Enum):
    EMAIL = "מייל"
    FIRST_NAME = "שם פרטי"
    LAST_NAME = "שם משפחה"
    COMPANY = "פלוגה"

    @staticmethod
    def is_valid(order: str) -> bool:
        return order in UserOrderBy._member_names_


class PersonnelOrderBy(Enum):
    ID = "מס' אישי"
    FIRST_NAME = "שם פרטי"
    LAST_NAME = "שם משפחה"
    COMPANY = "פלוגה"
    PLATOON = "מחלקה"

    @staticmethod
    def is_valid(order: str) -> bool:
        return order in PersonnelOrderBy._member_names_
