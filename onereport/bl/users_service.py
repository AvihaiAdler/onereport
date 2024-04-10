import datetime

from flask_sqlalchemy.pagination import Pagination
from flask import request, current_app
from flask_login import current_user
from onereport.dto.personnel_dto import PersonnelDTO
from onereport.dto.report_dto import ReportDTO
from onereport.data.misc import Company, Active, Platoon
from onereport.data.model import Personnel, Report
from onereport.dal import personnel_dal, report_dal, Order, PersonnelOrderBy
from onereport.exceptions import (
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    InternalServerError,
)
from onereport.controller.forms import PersonnelSortForm, PersonnelUpdateForm, UpdateReportForm


def get_all_personnel(
    form: PersonnelSortForm, company: str, order_by: str, order: str, /
) -> list[PersonnelDTO]:
    """
    Raises:
        BadRequestError,
        NotFoundError
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
        current_app.logger.error(f"invalid order_by {order_by}")
        raise BadRequestError(f"מיון לפי {order_by} אינו נתמך")

    if not Order.is_valid(order):
        current_app.logger.error(f"invalid order {order}")
        raise BadRequestError(f"סדר {order} אינו נתמך")
    
    personnel = personnel_dal.find_all_active_personnel_by_company(
        Company[company], PersonnelOrderBy[order_by], Order[order]
    )

    if not personnel:
        current_app.logger.debug(f"there are no visible personnel for {current_user}")
        raise NotFoundError(
            f"אין חיילים.ות במאגר השייכים לפלוגה {Company[company].value}"
        )

    return [PersonnelDTO(p) for p in personnel]


def update_personnel(form: PersonnelUpdateForm, id: str, /) -> PersonnelDTO:
    """
    Raises:
        BadRequestError,
        NotFoundError,
        ForbiddenError,
        InternalServerError
    """
    if form is None:
        current_app.logger.error(f"invalid form {form}")
        raise BadRequestError("form must not be None")

    old_personnel = personnel_dal.find_personnel_by_id(id)
    if old_personnel is None:
        current_app.logger.error(
            f"{current_user} tried to update a non exisiting personnel with id {id}"
        )
        raise NotFoundError(f"המס' האישי {id} אינו במסד הנתונים")

    if form.is_submitted():
        if not Active.is_valid(form.active.data):
            current_app.logger.error(f"invalid active {form.active.data}")
            raise BadRequestError("ערך פעיל אינו תקין")
        
        if not Platoon.is_valid(form.platoon.data):
            current_app.logger.error(f"invalid company {form.platoon.data}")
            raise BadRequestError("מחלקה אינה תקינה")
        
        personnel = Personnel(
            old_personnel.id,
            form.first_name.data.strip(),
            form.last_name.data.strip(),
            current_user.company,
            form.platoon.data,
        )

        # User tries to set itself to 'inactive' state
        if (
            personnel.id == current_user.id
            and Active.get_value_as_bool(form.active.data) != current_user.active
        ):
            current_app.logger.warning(f"{current_user} tried to deactivate themselves")
            raise ForbiddenError("אינך רשאי.ת לבצע פעולה זו")

        personnel.active = Active[form.active.data] == Active.ACTIVE
        # to ensure USERs cannot update Personnel::company
        personnel.company = old_personnel.company

        if not personnel_dal.update(old_personnel, personnel):
            current_app.logger.error(f"{current_user} failed to update {old_personnel}")
            raise InternalServerError("שגיאת שרת")

        current_app.logger.info(f"{current_user} successfully updated {old_personnel}")

    return PersonnelDTO(old_personnel)


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
        current_app.logger.error(f"invalid form {form}")
        raise BadRequestError("form must not be None")

    if not Company.is_valid(company):
        current_app.logger.error(f"invalid company {company}")
        raise BadRequestError("פלוגה אינה תקינה")

    if not PersonnelOrderBy.is_valid(order_by):
        current_app.logger.error(f"invalid order_by {order_by}")
        raise BadRequestError(f"מיון לפי {order_by} אינו נתמך")

    if not Order.is_valid(order):
        current_app.logger.error(f"invalid order {order}")
        raise BadRequestError(f"סדר {order} אינו נתמך")

    report = report_dal.find_report_by_date_and_company(
        datetime.date.today(), Company[company]
    )

    # no existing report for the current day
    if report is None:
        report = Report(Company[company].name)
        if not report_dal.save(report):
            current_app.logger.error(
                f"{current_user} failed to create a report for company: {company} at {datetime.date.today()}"
            )
            raise InternalServerError("שגיאת שרת")

        current_app.logger.info(f"{current_user} successfully created {report}")

    personnel = personnel_dal.find_all_active_personnel_by_company(
        Company[company], PersonnelOrderBy[order_by], Order[order]
    )
    if not personnel:
        current_app.logger.debug(f"no visibale personnel for {current_user}")
        raise NotFoundError(
            f"אין חיילים.ות במאגר השייכים לפלוגה {Company[company].value}"
        )

    # there is an exisiting report for the day
    if form.validate_on_submit():
        presence = {p for p in personnel if p.id in request.form}
        if not report_dal.update(report, presence):
            current_app.logger.error(f"{current_user} failed to update the report {report}")
            raise InternalServerError(
                f"הדוח ליום {datetime.date.today()} לא נשלח", category="danger"
            )

        current_app.logger.info(f"{current_user} successfully updated the report {report}")

    return [(PersonnelDTO(p), p in report.presence) for p in personnel]


def get_report(id: int, company: str, /) -> ReportDTO:
    """
    Raises:
        BadRequestError,
        NotFoundError
    """
    if not Company.is_valid(company):
        current_app.logger.error(f"invalid company {company}")
        raise BadRequestError("פלוגה אינה תקינה")

    report = report_dal.find_report_by_id_and_company(id, Company[company])
    if report is None:
        current_app.logger.error(
            f"{current_user} tried to get a non existing report with id {id} for company {current_user.company}"
        )
        raise NotFoundError(f"הדוח {id} אינו במסד הנתונים")

    personnel = personnel_dal.find_all_personnel_by_company_dated_before(
        Company[company], datetime.date.today(), PersonnelOrderBy.LAST_NAME, Order.ASC
    )
    if personnel is None:
        current_app.logger.debug(
            f"no visibale personnel in company {company} for {current_user}"
        )
        raise NotFoundError(
            f"אין חיילים.ות במאגר השייכים לפלוגה {Company[company].value}"
        )
    return ReportDTO(report, personnel)


def get_all_reports(company: str, order: str, page: str, per_page: str, /) -> Pagination:
    """
    Raises:
        BadRequestError,
        NotFoundError
    """
    if not Company.is_valid(company):
        current_app.logger.error(f"invalid company {company}")
        raise BadRequestError("פלוגה אינה תקינה")

    if not Order.is_valid(order):
        current_app.logger.error(f"invalid order {order}")
        raise BadRequestError(f"סדר {order} אינו נתמך")
    
    try:
        int(page)
    except ValueError:
        raise BadRequestError(f"הערך {page} עבור דף הינו שגוי")

    try:
        int(per_page)
    except ValueError:
        raise BadRequestError(f"הערך {page} עבור כמות עצמים בדף הינו שגוי")

    reports = report_dal.find_all_reports_by_company(Company[company], Order[order], int(page), int(per_page))
    if not reports.items:
        current_app.logger.debug(
            f"no reports for company: {company}, requested by: {current_user}"
        )
        raise NotFoundError(f"אין דוחות עבור פלוגה {Company[company].value}")

    return reports
