from onereport import app
from onereport.data.misc import Company
from onereport.dal import personnel_dal, user_dal
from onereport.dal.order_attr import Order, PersonnelOrderBy, UserOrderBy
from onereport.dto.user_dto import UserDTO
from onereport.dto.personnel_dto import PersonnelDTO
from onereport.exceptions.exceptions import (
    BadRequestError,
    NotFoundError,
)
from onereport.forms import PersonnelListForm


def get_all_users(order_by: str, order: str, /) -> list[UserDTO]:
    """
    Raises:
        BadRequestError,
        NotFoundError
    """
    if not UserOrderBy.is_valid(order_by):
        app.logger.error(f"invalid order_by: {order_by}")
        raise BadRequestError(f"מיון לפי {order_by} אינו נתמך")

    if not Order.is_valid(order):
        app.logger.error(f"invalid order: {order}")
        raise BadRequestError(f"סדר {order} אינו נתמך")

    users = user_dal.find_all_users(UserOrderBy[order_by], Order[order])
    if not users:
        app.logger.warning("USER table is empty")
        raise NotFoundError("רשימת המשתמשים הינה ריקה")

    return [UserDTO(user) for user in users]


def get_all_personnel(
    form: PersonnelListForm, company: str, order_by: str, order: str, /
) -> list[PersonnelDTO]:
    """
    Raises:
        BadRequestError,
        NotFoundError
    """
    if form is None:
        app.logger.error(f"invalid form {form}")
        raise BadRequestError("form must not be None")

    if not Company.is_valid(company):
        app.logger.error(f"invalid company {company}")
        raise BadRequestError("פלוגה אינה תקינה")
    
    if not PersonnelOrderBy.is_valid(order_by):
        app.logger.error(f"invalid order_by: {order_by}")
        raise BadRequestError(f"מיון לפי {order_by} אינו נתמך")

    if not Order.is_valid(order):
        app.logger.error(f"invalid order: {order}")
        raise BadRequestError(f"סדר {order} אינו נתמך")

    if form.validate_on_submit():
        order_by = form.order_by.data
        order = form.order.data
        company = form.company.data

    personnel = personnel_dal.find_all_personnel_by_company(
        Company[company], PersonnelOrderBy[order_by], Order[order]
    )
    if not personnel:
        app.logger.warning(f"there are no personnel for company {company}")
        # raise NotFoundError(f"לא נמצאו חיילים.ות עבור פלוגה {Company[company].value}")

    return [PersonnelDTO(p) for p in personnel]
