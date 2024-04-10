from onereport.bl import managers_service
from onereport.controller import forms
from onereport.dal.order_attr import Order, PersonnelOrderBy, UserOrderBy
from onereport.data import misc
from flask import (
    Blueprint,
    url_for,
    redirect,
    flash,
    render_template,
    request,
    current_app
)
from flask_login import current_user, login_required
from onereport.exceptions import (
    BadRequestError,
    ForbiddenError,
    UnauthorizedError,
    InternalServerError,
    NotFoundError,
)
import datetime
from onereport.controller.util import generate_url, not_permitted


managers = Blueprint("managers", __name__)


@managers.route("/onereport/managers/personnel/register", methods=["GET", "POST"])
@login_required
def register_personnel() -> str:
    if not_permitted(current_user.role, misc.Role.MANAGER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    form = forms.PersonnelRegistrationFrom()
    try:
        personnel = managers_service.register_personnel(form)
        if request.method == "GET":
            return render_template("personnel/personnel_registration.html", form=form)

        flash(
            f"החייל.ת {' '.join((personnel.first_name, personnel.last_name))} נוסף.ה בהצלחה",
            category="success",
        )
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)
    except ForbiddenError as fe:
        return render_template("errors/error.html", error=fe)
    except InternalServerError as ie:
        return render_template("errors/error.html", error=ie)

    return redirect(url_for("common.home"))


@managers.route("/onereport/managers/users/<id>/register", methods=["GET", "POST"])
@login_required
def register_user(id: str) -> str:
    if not_permitted(current_user.role, misc.Role.MANAGER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    form = forms.UserRegistrationFrom()
    try:
        personnel = managers_service.register_user(form, id)
        if request.method == "GET":
            form.id.data = personnel.id
            form.first_name.data, form.last_name.data = (
                personnel.first_name,
                personnel.last_name,
            )
            form.company.data, form.platoon.data = personnel.company, personnel.platoon

            return render_template("users/user_registration.html", form=form)

        flash(
            f"המשתמש.ת {' '.join((personnel.first_name, personnel.last_name))} נרשמה בהצלחה",
            category="success",
        )
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)
    except NotFoundError as ne:
        return render_template("errors/error.html", error=ne)
    except ForbiddenError as fe:
        return render_template("errors/error.html", error=fe)
    except InternalServerError as ie:
        return render_template("errors/error.html", error=ie)

    return redirect(
        url_for(generate_url(current_user.role, "get_all_personnel"), id=id)
    )


@managers.route("/onereport/managers/personnel/<id>/update", methods=["GET", "POST"])
@login_required
def update_personnel(id: str) -> str:
    if not_permitted(current_user.role, misc.Role.MANAGER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    form = forms.PersonnelUpdateForm()
    try:
        personnel = managers_service.update_personnel(form, id)
        if request.method == "GET":
            form.id.data = personnel.id
            form.first_name.data, form.last_name.data = (
                personnel.first_name,
                personnel.last_name,
            )
            form.company.data, form.platoon.data = (
                misc.Company(personnel.company).name,
                misc.Platoon(personnel.platoon).name,
            )
            form.active.data = misc.Active.get_name(personnel.active)

            return render_template("personnel/personnel.html", form=form)
        flash(
            f"החייל.ת {' '.join((personnel.first_name, personnel.last_name))} עודכן בהצלחה",
            category="success",
        )
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)
    except NotFoundError as ne:
        return render_template("errors/error.html", error=ne)
    except ForbiddenError as fe:
        return render_template("errors/error.html", error=fe)
    except InternalServerError as ie:
        return render_template("errors/error.html", error=ie)

    return redirect(url_for(generate_url(current_user.role, "get_all_personnel")))


@managers.route("/onereport/managers/users/<email>/update", methods=["GET", "POST"])
@login_required
def update_user(email: str) -> str:
    if not_permitted(current_user.role, misc.Role.MANAGER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    form = forms.UserUpdateForm()
    try:
        user = managers_service.update_user(form, email)
        if request.method == "GET":
            form.id.data = user.id
            form.email.data = user.email
            form.first_name.data, form.last_name.data = user.first_name, user.last_name
            form.company.data, form.platoon.data = (
                misc.Company(user.company).name,
                misc.Platoon(user.platoon).name,
            )
            form.role.data = misc.Role.get_name(user.role)
            form.active.data = user.active

            return render_template("users/user.html", form=form)

        flash(
            f"המשתמש.ת {' '.join((user.first_name, user.last_name))} עודכן בהצלחה",
            category="success",
        )
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)
    except NotFoundError as ne:
        return render_template("errors/error.html", error=ne)
    except ForbiddenError as fe:
        return render_template("errors/error.html", error=fe)
    except InternalServerError as ie:
        return render_template("errors/error.html", error=ie)

    return redirect(url_for(generate_url(current_user.role, "get_all_users")))


@managers.route("/onereport/managers/users", methods=["GET", "POST"])
@login_required
def get_all_users() -> str:
    if not_permitted(current_user.role, misc.Role.MANAGER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    order_by = request.args.get("order_by", default=UserOrderBy.COMPANY.name)
    order = request.args.get("order", default=Order.ASC.name)

    try:
        users = managers_service.get_all_users(order_by, order)
        return render_template("users/users.html", users=users)
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)
    except NotFoundError as ne:
        return render_template("errors/error.html", error=ne)


@managers.route("/onereport/managers/personnel", methods=["GET", "POST"])
@login_required
def get_all_personnel() -> str:
    if not_permitted(current_user.role, misc.Role.MANAGER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    company = request.args.get("company", default=current_user.company)
    order_by = request.args.get("order_by", default=PersonnelOrderBy.LAST_NAME.name)
    order = request.args.get("order", default=Order.ASC.name)

    form = forms.PersonnelSortForm()
    try:
        personnel = managers_service.get_all_personnel(
            form, company, order_by, order
        )

        return render_template(
            "personnel/personnel_list.html", form=form, personnel=personnel, company=misc.Company
        )
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)
    except NotFoundError as ne:
        return render_template("errors/error.html", error=ne)


@managers.route("/onereport/managers/report", methods=["GET", "POST"])
@login_required
def create_report() -> str:
    if not_permitted(current_user.role, misc.Role.MANAGER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    order_by = request.args.get("order_by", default=PersonnelOrderBy.LAST_NAME.name)
    order = request.args.get("order", default=Order.ASC.name)

    form = forms.UpdateReportForm()
    try:
        personnel = managers_service.report(form, current_user.company, order_by, order)
        if request.method == "GET":
            return render_template(
                "reports/editable_report.html",
                form=form,
                personnel_presence_list=personnel,
                today=datetime.date.today(),
            )

        flash(f"הדוח ליום {datetime.date.today()} נשלח בהצלחה", category="success")
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)
    except NotFoundError as ne:
        return render_template("errors/error.html", error=ne)
    except InternalServerError as ie:
        return render_template("errors/error.html", error=ie)

    return redirect(
        url_for(
            generate_url(current_user.role, "create_report"),
            order_by=order_by,
            order=order,
        )
    )


@managers.get("/onereport/managers/reports")
@login_required
def get_all_reports() -> str:
    if not_permitted(current_user.role, misc.Role.MANAGER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    company = request.args.get("company", current_user.company)
    order = request.args.get("order", Order.DESC.name)
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "20")

    try:
        pagination = managers_service.get_all_reports_for(
            company, order, page, per_page
        )
        return render_template(
            "reports/reports.html",
            pagination=pagination,
            company=misc.Company,
            current_company=(
                misc.Company[company].value if misc.Company.is_valid(company) else ""
            ),
            page=page,
            per_page=per_page,
        )
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)


@managers.get("/onereport/managers/reports/unified")
@login_required
def get_all_unified_reports() -> str:
    if not_permitted(current_user.role, misc.Role.MANAGER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    order = request.args.get("order", Order.DESC.name)
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "20")

    try:
        pagination = managers_service.get_all_reports(order, page, per_page)
        return render_template(
            "reports/unified_reports.html",
            pagination=pagination,
            page=page,
            per_page=per_page,
        )
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)


@managers.get("/onereport/managers/report/<int:id>")
@login_required
def get_report(id: int) -> str:
    if not_permitted(current_user.role, misc.Role.MANAGER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    company = request.args.get("company", current_user.company)

    try:
        report = managers_service.get_report(id, company)
        return render_template("reports/uneditable_report.html", report=report)
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)
    except NotFoundError as ne:
        return render_template("errors/error.html", error=ne)


@managers.get("/onereport/managers/report/unified/<date>")
@login_required
def get_unified_report(date: str) -> str:
    if not_permitted(current_user.role, misc.Role.MANAGER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    order_by = request.args.get("order_by", default=PersonnelOrderBy.LAST_NAME.name)
    order = request.args.get("order", default=Order.ASC.name)

    try:
        report = managers_service.get_unified_report(date, order_by, order)
        return render_template("reports/unified_report.html", report=report)
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)
    except NotFoundError as ne:
        return render_template("errors/error.html", error=ne)
    except InternalServerError as ie:
        return render_template("errors/error.html", error=ie)
