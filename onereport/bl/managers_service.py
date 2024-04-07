from typing import Tuple
from onereport import app
from flask import request
from flask_login import current_user
from onereport.data.misc import Active, Company, Role
from onereport.data.model import Personnel, User, Report
from onereport.dto.personnel_dto import PersonnelDTO
from onereport.dto.report_dto import ReportDTO
from onereport.dto.user_dto import UserDTO
from onereport.dal import personnel_dal, user_dal, report_dal
from onereport.dal.order_attr import PersonnelOrderBy, Order, UserOrderBy
from onereport.exceptions import (
    BadRequestError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
)
from onereport.forms import (
    PersonnelListForm,
    PersonnelRegistrationFrom,
    PersonnelUpdateForm,
    UpdateReportForm,
    UserRegistrationFrom,
    UserUpdateForm,
)
import datetime


def register_personnel(form: PersonnelRegistrationFrom) -> PersonnelDTO | None:
    """
    Raises:
        BadRequestError,
        ForbiddenError,
        InternalServerError
    """
    if form is None:
        app.logger.error(f"invalid form {form}")
        raise BadRequestError("form must not be None")

    if form.validate_on_submit():
        # "      1" will be technically valid - but i couldn't care less
        personnel = Personnel(
            form.id.data.strip(),
            form.first_name.data.strip(),
            form.last_name.data.strip(),
            form.company.data,
            form.platoon.data,
        )
        old_personnel = personnel_dal.find_personnel_by_id(personnel.id)
        match old_personnel:
            case None:  # no such personnel exists
                if not personnel_dal.save(personnel):
                    app.logger.error(f"failed to save {personnel} for {current_user}")
                    raise InternalServerError("שגיאת שרת")

                app.logger.debug(f"{current_user} successfully registered {personnel}")
            case op if not op.active:  # such personnel exists but is inactive
                if not personnel_dal.update(op, personnel):
                    app.logger.error(f"{current_user} failed to update {op}")
                    raise InternalServerError("שגיאת שרת")

                app.logger.info(f"{current_user} successfully updated {op}")
            case _:  # such personnel exists and active
                raise ForbiddenError(
                    f"חייל.ת עם מס' אישי {old_personnel.id} כבר נמצא במערכת"
                )
        return PersonnelDTO(personnel)

    return None


def register_user(form: UserRegistrationFrom, id: str, /) -> PersonnelDTO:
    """
    Raises:
        BadRequestError,
        NotFoundError,
        ForbiddenError,
        InternalServerError
    """
    if form is None:
        app.logger.error(f"invalid form {form}")
        raise BadRequestError("form must not be None")

    personnel = personnel_dal.find_personnel_by_id(id)
    if personnel is None:
        app.logger.error(
            f"{current_user} tried to register a non exiting user with id {id}"
        )
        raise NotFoundError(f"המס' האישי {id} אינו במסד הנתונים")

    if form.validate_on_submit():
        user = User(
            personnel.id,
            form.email.data.strip(),
            form.first_name.data.strip(),
            form.last_name.data.strip(),
            form.role.data,
            form.company.data,
            form.platoon.data,
        )

        if Role.get_level(current_user.role) > Role.get_level(user.role):
            app.logger.error(
                f"{current_user} with permision level {Role.get_level(current_user.role)} tried to register a user with permission level {Role.get_level(form.role.data)}"
            )
            raise ForbiddenError("אינך רשאי.ת לבצע פעולה זו")

        old_user = user_dal.find_user_by_email(user.email)
        match old_user:
            case None:  # no such user exists
                # delete the personnel since it has the same id as the newly created user
                if not personnel_dal.delete(personnel):
                    app.logger.error(f"failed to delete {personnel} for {current_user}")
                    raise InternalServerError("שגיאת שרת")

                app.logger.info(f"{current_user} successfully deleted {personnel}")

                # save the newly created user
                if not user_dal.save(user):
                    app.logger.error(f"failed to save {personnel} for {current_user}")
                    # try to reinstate personnel
                    # if this fails we're in as irrecoverable state
                    if not personnel_dal.save(personnel):
                        app.logger.critical(
                            f"failed to reinstate previous state. personnel has been deleted yet no user has been saved, and attemps to resave the old personnel fails\n{personnel}"
                        )
                    raise InternalServerError("שגיאת שרת")

                app.logger.info(f"{current_user} successfully deleted {personnel}")
            case ou if not ou.active:  # such user exists but is inactive
                if not user_dal.update(ou, user):
                    app.logger.error(f"{current_user} failed to update {old_user}")
                    raise InternalServerError("שגיאת שרת")

                app.logger.info(f"{current_user} successfully updated {old_user}")
            case _:
                app.logger.error(
                    f"{current_user} tried to register {user} with the same email as {old_user}"
                )
                raise ForbiddenError("משתמש.ת עם כתובת מייל זו כבר רשום.ה במערכת")
        return PersonnelDTO.from_user(user)
    return PersonnelDTO(personnel)


def update_personnel(form: PersonnelUpdateForm, id: str, /) -> PersonnelDTO:
    """
    Raises:
        BadRequestError,
        NotFoundError,
        ForbiddenError,
        InternalServerError
    """
    if form is None:
        app.logger.error(f"invalid form {form}")
        raise BadRequestError("form must not be None")

    old_personnel = personnel_dal.find_personnel_by_id(id)
    if old_personnel is None:
        app.logger.error(
            f"{current_user} tried to register a non exiting user with id {id}"
        )
        raise NotFoundError(f"המס' האישי {id} אינו במסד הנתונים")

    if form.validate_on_submit():
        personnel = Personnel(
            old_personnel.id,
            form.first_name.data.strip(),
            form.last_name.data.strip(),
            form.company.data,
            form.platoon.data,
        )

        # User tries to set itself to 'inactive' state
        if (
            personnel.id == current_user.id
            and Active.get_value_as_bool(form.active.data) != current_user.active
        ):
            app.logger.warning(f"{current_user} tried to deactivate themselves")
            raise ForbiddenError("אינך רשאי.ת לבצע פעולה זו")

        personnel.active = Active[form.active.data] == Active.ACTIVE

        if not personnel_dal.update(old_personnel, personnel):
            app.logger.error(f"{current_user} failed to update {old_personnel}")
            raise InternalServerError("שגיאת שרת")

        app.logger.info(f"{current_user} successfully updated {old_personnel}")

    return PersonnelDTO(old_personnel)


def demote(user: User) -> None:
    """
    Raises:
        ForbiddenError,
        InternalServerError
    """
    if current_user.id == user.id:
        app.logger.warning(f"{current_user} tried to demote themselves")
        raise ForbiddenError("אינך רשאי.ת לבצע פעולה זו")

    if not user_dal.delete(user):  # delete user since it has the same id
        app.logger.error(f"{current_user} failed to delete {user}")
        raise InternalServerError("הפעולה לא הושלמה בהצלחה")

    app.logger.info(f"{current_user} successfully deleted {user}")

    personnel = Personnel(
        user.id, user.first_name, user.last_name, user.company, user.platoon
    )
    if not personnel_dal.save(personnel):
        app.logger.error(
            f"{current_user} failed to save the personnel {personnel}. demotion failed"
        )

        # if this operation failed we're in an irrecoverable state
        if not user_dal.save(user):
            app.logger.critical(
                f"failed to reinstate previous state. user has been deleted yet no personnel has been saved, and attemps to resave the old user fails\n{user}"
            )
        raise InternalServerError("שגיאת שרת")

    app.logger.info(
        f"{current_user} successfuly demoted {user} to a personnel {personnel}"
    )


def update_user(form: UserUpdateForm, email: str, /) -> UserDTO:
    """
    Raises:
        BadRequestError,
        NotFoundError,
        ForbiddenError,
        InternalServerError
    """
    if form is None:
        app.logger.error(f"invalid form {form}")
        raise BadRequestError("form must not be None")

    old_user = user_dal.find_user_by_email(email)
    if old_user is None:
        app.logger.error(
            f"{current_user} tried to update non exisiting user with email {email}"
        )
        raise NotFoundError("המשתמש אינו במסד הנתונים")

    if form.validate_on_submit():
        if form.delete.data:
            try:
                demote(old_user)
            except ForbiddenError:
                raise
            except InternalServerError:
                raise

        user = User(
            old_user.id,
            form.email.data,
            form.first_name.data.strip(),
            form.last_name.data.strip(),
            form.role.data,
            form.company.data,
            form.platoon.data,
        )

        if Role.get_level(current_user.role) > Role.get_level(user.role):
            app.logger.warning(
                f"{current_user} with permision level {Role.get_level(current_user.role)} tried to register a user with permission level {Role.get_level(user.role)}"
            )
            raise ForbiddenError("אינך רשאי.ת לבצע פעולה זו")

        if (
            user.id == current_user.id
            and Active.get_value_as_bool(form.active.data) != current_user.active
        ):
            app.logger.warning(f"{current_user} tried to deactivate themselves {user}")
            raise ForbiddenError("אינך רשאי.ת לבצע פעולה זו")

        user.active = Active[form.active.data] == Active.ACTIVE

        if user.id == current_user.id and Role.get_level(
            current_user.role
        ) != Role.get_level(user.role):
            app.logger.warning(f"{current_user} tried to change their role to {user}")
            raise ForbiddenError("אינך רשאי.ת לבצע פעולה זו")

        if not user_dal.update(old_user, user):
            app.logger.error(f"{current_user} failed to update {old_user}")
            raise InternalServerError("שגיאת שרת")
        app.logger.info(f"{current_user} successfully updated {old_user}")

    return UserDTO(old_user)


def get_all_users(order_by: str, order: str, /) -> list[UserDTO]:
    """
    Raises:
        BadRequestError,
        NotFoundError
    """
    if not PersonnelOrderBy.is_valid(order_by):
        app.logger.error(f"invalid order_by {order_by}")
        raise BadRequestError(f"מיון לפי {order_by} אינו נתמך")

    if not Order.is_valid(order):
        app.logger.error(f"invalid order {order}")
        raise BadRequestError(f"סדר {order} אינו נתמך")

    users = user_dal.find_all_active_users(UserOrderBy[order_by], Order[order])
    if not users:
        app.logger.debug(f"there are no visible users for {current_user}")
        raise NotFoundError("לא נמצאו משתמשים")

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
        app.logger.error(f"invalid order_by {order_by}")
        raise BadRequestError(f"מיון לפי {order_by} אינו נתמך")

    if not Order.is_valid(order):
        app.logger.error(f"invalid order {order}")
        raise BadRequestError(f"סדר {order} אינו נתמך")

    if form.validate_on_submit():
        order_by = form.order_by.data
        order = form.order.data
        company = form.company.data

    personnel = personnel_dal.find_all_active_personnel_by_company(
        Company[company], PersonnelOrderBy[order_by], Order[order]
    )
    if not personnel:
        app.logger.debug(
            f"there are no visible personnel in company {company} for {current_user}"
        )
        # raise NotFoundError(f"לא נמצאו חיילים.ות עבור פלוגה {Company[Company].value}")

    return [PersonnelDTO(p) for p in personnel]


def report(
    form: UpdateReportForm, company: str, order_by: str, order: str, /
) -> list[PersonnelDTO]:
    """
    Raises:
        BadRequestError,
        NotFoundError,
        InternalServerError,
    """
    if form is None:
        app.logger.error(f"invalid form {form}")
        raise BadRequestError("form must not be None")

    if not Company.is_valid(company):
        app.logger.error(f"invalid company {company}")
        raise BadRequestError("פלוגה אינה תקינה")

    if not PersonnelOrderBy.is_valid(order_by):
        app.logger.error(f"invalid order_by {order_by}")
        raise BadRequestError(f"מיון לפי {order_by} אינו נתמך")

    if not Order.is_valid(order):
        app.logger.error(f"invalid order {order}")
        raise BadRequestError(f"סדר {order} אינו נתמך")

    report = report_dal.find_report_by_date_and_company(
        datetime.date.today(), Company[company]
    )

    # no existing report for the current day
    if report is None:
        report = Report(Company[company].name)
        if not report_dal.save(report):
            app.logger.error(
                f"{current_user} failed to create a report for company: {company} at {datetime.date.today()}"
            )
            raise InternalServerError("שגיאת שרת")
        app.logger.info(f"{current_user} successfully created {report}")

    personnel = personnel_dal.find_all_active_personnel_by_company(
        Company[company], PersonnelOrderBy[order_by], Order[order]
    )

    if not personnel:
        app.logger.debug(
            f"no visibale personnel in company {company} for {current_user}"
        )
        raise NotFoundError(
            f"אין חיילים.ות במאגר השייכים לפלוגה {Company[company].value}"
        )

    # there is an exisiting report for the day
    if form.validate_on_submit():
        presence = {p for p in personnel if p.id in request.form}
        if not report_dal.update(report, presence):
            app.logger.error(f"{current_user} failed to update the report {report}")
            raise InternalServerError(
                f"הדוח ליום {datetime.date.today()} לא נשלח", category="danger"
            )
        app.logger.info(f"{current_user} successfully updated the report {report}")

    return [(PersonnelDTO(p), p in report.presence) for p in personnel]


def get_report(id: str, company: str, /) -> ReportDTO:
    """
    Raises:
        BadRequestError,
        NotFoundError
    """
    if not Company.is_valid(company):
        app.logger.error(f"invalid company {company}")
        raise BadRequestError("פלוגה אינה תקינה")

    report = report_dal.find_report_by_id_and_company(id, Company[company])
    if report is None:
        app.logger.error(
            f"{current_user} tried to get a non existing report with id {id} for company {current_user.company}"
        )
        raise NotFoundError(f"הדוח {id} אינו במסד הנתונים")

    personnel = personnel_dal.find_all_personnel_by_company_dated_before(
        Company[company], datetime.date.today(), PersonnelOrderBy.LAST_NAME, Order.ASC
    )
    if personnel is None:
        app.logger.debug(
            f"no visibale personnel in company {company} for {current_user}"
        )
        raise NotFoundError(
            f"אין חיילים.ות במאגר השייכים לפלוגה {Company[company].value}"
        )
    return ReportDTO(report, personnel)


def get_all_reports(company: str, order: str, /) -> list[Tuple[str, datetime.date]]:
    """
    Raises:
        BadRequestError,
        NotFoundError:
    """
    if not Company.is_valid(company):
        app.logger.error(f"invalid company {company} for {current_user}")
        raise BadRequestError("פלוגה אינה תקינה")

    if not Order.is_valid(order):
        app.logger.error(f"invalid order {order}")
        raise BadRequestError(f"סדר {order} אינו נתמך")

    reports = report_dal.find_all_reports_by_company(Company[company], Order[order])
    if not reports:
        app.logger.debug(f"no visible reports for company {company} for {current_user}")
        # raise NotFoundError(f"לא נמצאו דוחות עבור פלוגה {Company[company].value}")

    return [(report.id, report.date) for report in reports]
