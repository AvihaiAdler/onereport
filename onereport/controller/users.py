from onereport.controller import forms
from onereport.controller.util import not_permitted
from onereport.dal.order_attr import Order, PersonnelOrderBy
from onereport.data import misc
from onereport.bl import users_service
from onereport.exceptions import (
    BadRequestError,
    ForbiddenError,
    UnauthorizedError,
    InternalServerError,
    NotFoundError,
)
from flask import (
    Blueprint,
    url_for,
    redirect,
    flash,
    render_template,
    request,
    current_app,
)
from flask_login import current_user
import datetime


users = Blueprint("users", __name__)


@users.route("/onereport/users/personnel", methods=["GET", "POST"])
# @login_required
def get_all_personnel() -> str:
    if not_permitted(current_user.role, misc.Role.USER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    order_by = request.args.get("order_by", default=PersonnelOrderBy.LAST_NAME.name)
    order = request.args.get("order", default=Order.ASC.name)

    form = forms.PersonnelSortForm()
    try:
        personnel = users_service.get_all_personnel(
            form, current_user.company, order_by, order
        )

        return render_template(
            "personnel/personnel_list.html",
            form=form,
            personnel=personnel,
            company=misc.Company,
        )
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)
    except NotFoundError as ne:
        return render_template("errors/error.html", error=ne)


@users.route("/onereport/users/personnel/<id>/update", methods=["GET", "POST"])
# @login_required
def update_personnel(id: str) -> str:
    if not_permitted(current_user.role, misc.Role.USER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    form = forms.PersonnelUpdateForm()
    try:
        personnel = users_service.update_personnel(form, id)
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

    return redirect(url_for("users.get_all_personnel"))


@users.route("/onereport/users/report", methods=["GET", "POST"])
# @login_required
def create_report() -> str:
    if not_permitted(current_user.role, misc.Role.USER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    order_by = request.args.get("order_by", default=PersonnelOrderBy.LAST_NAME.name)
    order = request.args.get("order", default=Order.ASC.name)

    form = forms.UpdateReportForm()
    try:
        personnel = users_service.report(form, current_user.company, order_by, order)
        if request.method == "GET":
            return render_template(
                "reports/editable_report.html",
                form=form,
                personnel_presence_list=personnel,
                today=datetime.date.today(),
            )

        flash(f"הדוח ליום {datetime.date.today()} נשלח בהצלחה", category="success")
        return redirect(url_for("users.create_report", order_by=order_by, order=order))
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)
    except NotFoundError as ne:
        return render_template("errors/error.html", error=ne)
    except InternalServerError as ie:
        return render_template("errors/error.html", error=ie)


@users.get("/onereport/users/reports")
# @login_required
def get_all_reports() -> str:
    if not_permitted(current_user.role, misc.Role.USER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    order = request.args.get("order", default=Order.DESC.name)
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "20")

    try:
        pagination = users_service.get_all_reports(
            current_user.company, order, page, per_page
        )
        return render_template(
            "reports/reports.html",
            current_company=current_user.company,
            pagination=pagination,
            page=page,
            per_page=per_page,
        )
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)
    except NotFoundError as ne:
        return render_template("errors/error.html", error=ne)


@users.get("/onereport/users/report/<int:id>")
# @login_required
def get_report(id: int) -> str:
    if not_permitted(current_user.role, misc.Role.USER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    try:
        report = users_service.get_report(id, current_user.company)
        return render_template("reports/uneditable_report.html", report=report)
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)
    except NotFoundError as ne:
        return render_template("errors/error.html", error=ne)
