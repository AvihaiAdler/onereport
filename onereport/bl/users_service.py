import datetime
from typing import Tuple
from onereport import app
from flask import request
from flask_login import current_user
from dto.personnel_dto import PersonnelDTO
from data.misc import Company, Active
from data.model import Personnel, Report
from dal.order_attr import Order, PersonnelOrderBy
from onereport.dal import personnel_dal, report_dal
from onereport.exceptions.exceptions import (
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    InternalServerError,
)
from forms import PersonnelListForm, PersonnelUpdateForm, UpdateReportForm
from onereport.dto.report_dto import ReportDTO


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

    personnel = personnel_dal.find_all_active_personnel_by_company(
        Company[company], PersonnelOrderBy[order_by], Order[order]
    )

    if not personnel:
        app.logger.debug(f"there are no visible personnel for {current_user}")
        raise NotFoundError(
            f"אין חיילים.ות במאגר השייכים לפלוגה {Company[company].value}"
        )

    app.logger.debug(
        f"passing {len(personnel)} personnel to personnel_list.html for {current_user}"
    )

    return [PersonnelDTO(p) for p in personnel]


def update_personnel(
    form: PersonnelUpdateForm, id: str, /
) -> Tuple[PersonnelDTO, bool]:
    """
    Raises:
        BadRequestError,
        NotFoundError,
        ForbiddenError
    """
    if form is None:
        app.logger.error(f"invalid form {form}")
        raise BadRequestError("form must not be None")

    old_personnel = personnel_dal.find_personnel_by_id(id)
    if old_personnel is None:
        app.logger.error(
            f"{current_user} tried to update a non exisiting personnel with id {id}"
        )
        raise NotFoundError(f"החייל {id} אינו במסד הנתונים")

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
            and Active[form.active.data] != current_user.active
        ):
            app.logger.warning(f"{current_user} tried to deactivate themselves")
            raise ForbiddenError("אינך רשאי.ת לבצע פעולה זו")

        personnel.active = Active[form.active.data] == Active.ACTIVE
        # to ensure users cannot update Personnel::company
        personnel.company = old_personnel.company
        old_personnel.update(personnel)
        if personnel_dal.update(personnel):
            app.logger.info(f"{current_user} successfully updated {old_personnel}")
            return (PersonnelDTO(old_personnel), True)

    app.logger.error(f"{current_user} failed to update {old_personnel}")
    return (PersonnelDTO(old_personnel), False)


def report(
    form: UpdateReportForm, company: str, order_by: str, order: str, /
) -> list[PersonnelDTO]:
    """
    Raises:
        BadRequestError,
        InternalServerError,
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

    report = report_dal.find_report_by_date_and_company(
        datetime.date.today(), Company[company]
    )

    # no existing report for the current day
    if report is None:
        report = Report(Company[company].name)
        if report_dal.save(report):
            app.logger.info(f"{current_user} successfully created {report}")
        else:
            app.logger.error(
                f"{current_user} failed to create a report for company: {company} at {datetime.date.today()}"
            )
            raise InternalServerError("שגיאת שרת")

    personnel = personnel_dal.find_all_active_personnel_by_company(
        Company[company], PersonnelOrderBy[order_by], Order[order]
    )
    if not personnel:
        app.logger.debug(f"no visibale personnel for {current_user}")
        raise NotFoundError(
            f"אין חיילים.ות במאגר השייכים לפלוגה {Company[company].value}"
        )

    # there is an exisitng report for the day
    if form.validate_on_submit():
        report.presence = {p for p in personnel if p.id in request.form}
        if report_dal.update(report):
            app.logger.info(f"{current_user} successfully updated the report {report}")
        else:
            app.logger.error(f"{current_user} failed to update the report {report}")
            raise InternalServerError(
                f"הדוח ליום {datetime.date.today()} לא נשלח", category="danger"
            )

    return [(PersonnelDTO(p), p in report.presence) for p in personnel]


def get_report(id: int, company: str, /) -> ReportDTO:
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

    return ReportDTO(report)


def get_all_reports(company: str, order: str, /) -> list[ReportDTO]:
    """
    Raises:
        BadRequestError,
        NotFoundError
    """
    if not Company.is_valid(company):
        app.logger.error(f"invalid company {company}")
        raise BadRequestError("פלוגה אינה תקינה")

    if not Order.is_valid(order):
        app.logger.error(f"invalid order {order}")
        raise BadRequestError(f"סדר {order} אינו נתמך")

    reports = report_dal.find_all_reports_by_company(Company[company], Order[order])
    if not reports:
        app.logger.debug(
            f"no reports for company: {company}, requested by: {current_user}"
        )
        raise NotFoundError(f"אין דוחות עבור פלוגה {Company[company].value}")

    return [ReportDTO(report) for report in reports]
