import json
from onereport.data.misc import Company
from onereport.dal import (
    personnel_dal,
    user_dal,
    report_dal,
    Order,
    UserOrderBy,
    PersonnelOrderBy,
)
from onereport.data import Personnel, User
from onereport.dto.user_dto import UserDTO
from onereport.dto.personnel_dto import PersonnelDTO
from onereport.exceptions import BadRequestError, NotFoundError, InternalServerError
from onereport.controller.forms import PersonnelSortForm, UploadPersonnelForm
from flask_login import current_user
from flask import current_app


def get_all_users(order_by: str, order: str, /) -> list[UserDTO]:
    """
    Raises:
        BadRequestError,
        NotFoundError
    """
    if not UserOrderBy.is_valid(order_by):
        current_app.logger.error(f"invalid order_by: {order_by}")
        raise BadRequestError(f"מיון לפי {order_by} אינו נתמך")

    if not Order.is_valid(order):
        current_app.logger.error(f"invalid order: {order}")
        raise BadRequestError(f"סדר {order} אינו נתמך")

    users = user_dal.find_all_users(UserOrderBy[order_by], Order[order])
    if not users:
        current_app.logger.warning("USER table is empty")
        raise NotFoundError("רשימת המשתמשים הינה ריקה")

    return [UserDTO(user) for user in users]


def get_all_personnel(
    form: PersonnelSortForm, company: str, order_by: str, order: str, /
) -> list[PersonnelDTO]:
    """
    Raises:
        BadRequestError
    """
    if form is None:
        current_app.logger.error(f"invalid form {form}")
        raise BadRequestError("form must not be None")

    if not Company.is_valid(company):
        current_app.logger.error(f"invalid company {company}")
        raise BadRequestError("פלוגה אינה תקינה")

    if form.is_submitted():
        order_by = form.order_by.data
        order = form.order.data

    if not PersonnelOrderBy.is_valid(order_by):
        current_app.logger.error(f"invalid order_by: {order_by}")
        raise BadRequestError(f"מיון לפי {order_by} אינו נתמך")

    if not Order.is_valid(order):
        current_app.logger.error(f"invalid order: {order}")
        raise BadRequestError(f"סדר {order} אינו נתמך")

    personnel = personnel_dal.find_all_personnel_by_company(
        Company[company], PersonnelOrderBy[order_by], Order[order]
    )
    if not personnel:
        current_app.logger.warning(f"there are no personnel for company {company}")

    return [PersonnelDTO(p) for p in personnel]


def delete_report(id: int) -> None:
    report = report_dal.find_report_by_id(id)

    if report is None:
        current_app.logger.error(f"{current_user} supplied a wrong id {id}")
        raise NotFoundError(f"הדוח {id} אינו קיים")

    if not report_dal.delete(report):
        raise InternalServerError(f"שגיאת שרת: הדוח {id} לא נמחק")


def delete_all_reports() -> None:
    reports = report_dal.find_all_reports()
    report_dal.delete_all(reports)

    current_app.logger.info(
        f"{current_user} deleted all reports\n{chr(10).join([report.__str__() for report in reports])}"
    )


def delete_all_personnel() -> None:
    personnel = personnel_dal.find_all_personnel(PersonnelOrderBy.ID, Order.ASC)
    users = user_dal.find_all_users(UserOrderBy.LAST_NAME, Order.ASC)

    user_dal.delete_all([u for u in users if u.id != current_user.id])
    personnel_dal.delete_all([p for p in personnel if p.id != current_user.id])

    current_app.logger.info(
        f"{current_user} deleted all users & personnel\n{chr(10).join([user.__str__() for user in users])}\n{chr(10).join([p.__str__() for p in personnel])}"
    )


def dict_to_personnel(personnel_dict: dict[str]) -> Personnel | None:
    if not personnel_dict:
        return None

    if personnel_dict.get("id", None) is None:
        return None
    if personnel_dict.get("first_name", None) is None:
        return None
    if personnel_dict.get("last_name", None) is None:
        return None
    if personnel_dict.get("company", None) is None:
        return None
    if personnel_dict.get("platoon", None) is None:
        return None

    return Personnel(
        personnel_dict["id"],
        personnel_dict["first_name"],
        personnel_dict["last_name"],
        personnel_dict["company"],
        personnel_dict["platoon"],
    )


def dict_to_user(user_dict: dict[str]) -> User | None:
    if not user_dict:
        return None

    if user_dict.get("id", None) is None:
        return None
    if user_dict.get("email", None) is None:
        return None
    if user_dict.get("first_name", None) is None:
        return None
    if user_dict.get("last_name", None) is None:
        return None
    if user_dict.get("role", None) is None:
        return None
    if user_dict.get("company", None) is None:
        return None
    if user_dict.get("platoon", None) is None:
        return None

    return User(
        user_dict["id"],
        user_dict["email"],
        user_dict["first_name"],
        user_dict["last_name"],
        user_dict["role"],
        user_dict["company"],
        user_dict["platoon"],
    )


def upload_personnel(form: UploadPersonnelForm) -> None:
    """
    Raises:
        BadRequestError,
        InternalServerError
    """
    if form is None:
        current_app.logger.error(f"invalid form {form}")
        raise BadRequestError("form must not be None")

    if form.validate_on_submit():
        file = form.file.data
        if file is None or not file:
            raise InternalServerError("שגיאת שרת")

        data = json.load(file.stream)
        personnel = list(
            filter(
                lambda p: p is not None,
                map(lambda p: dict_to_personnel(p), data.get("Personnel", [])),
            )
        )
        users = list(
            filter(
                lambda u: u is not None,
                map(lambda u: dict_to_user(u), data.get("Users", [])),
            )
        )

        if not personnel_dal.save_all(personnel):
            current_app.logger.warning("not all personnel were saved")
        else:
            current_app.logger.info(
                f"{current_user} uploaded {len(personnel)} personnel:\n{chr(10).join([p.__str__() for p in personnel])}"
            )

        if not user_dal.save_all(users):
            current_app.logger.warning("not all users were saved")
        else:
            current_app.logger.info(
                f"{current_user} uploaded {len(users)} personnel:\n{chr(10).join([user.__str__() for user in users])}"
            )
