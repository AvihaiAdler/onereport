from onereport.controller import forms
from onereport.controller.util import not_permitted
from onereport.data import misc
from onereport.bl import users_service
from onereport.exceptions import (
    BadRequestError,
    ForbiddenError,
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
    abort,
    current_app,
)
from flask_login import current_user, login_required
import datetime


users = Blueprint("users", __name__)


@users.route("/onereport/users/personnel", methods=["GET", "POST"])
@login_required
def get_all_personnel() -> str:
    if not_permitted(current_user.role, misc.Role.USER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

    order_by = request.args.get("order_by", default="LAST_NAME")
    order = request.args.get("order", default="ASC")

    form = forms.PersonnelListForm()
    try:
        personnel = users_service.get_all_personnel(
            form, current_user.company, order_by, order
        )
        if request.method == "GET":
            form.company.data = "F"
        
        return render_template(
            "personnel/personnel_list.html",
            form=form,
            personnel=personnel,
        )
    except BadRequestError as be:
        flash(f"{be}", category="danger")
    except NotFoundError as ne:
        flash(f"{ne}", category="info")
    return redirect(url_for("common.home"))


@users.route("/onereport/users/personnel/<id>/update", methods=["GET", "POST"])
@login_required
def update_personnel(id: str) -> str:
    if not_permitted(current_user.role, misc.Role.USER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

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
        flash(f"{be}", category="danger")
    except NotFoundError as ne:
        flash(f"{ne}", category="danger")
    except ForbiddenError as fe:
        flash(f"{fe}", category="danger")
    except InternalServerError as ie:
        flash(f"{ie}", category="danger")
    return redirect(url_for("users.get_all_personnel"))


@users.route("/onereport/users/report", methods=["GET", "POST"])
@login_required
def create_report() -> str:
    if not_permitted(current_user.role, misc.Role.USER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

    order_by = request.args.get("order_by", "LAST_NAME")
    order = request.args.get("order", "ASC")

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
        flash(f"{be}", category="danger")
    except NotFoundError as ne:
        flash(f"{ne}", category="danger")
    except InternalServerError as ie:
        flash(f"{ie}", category="danger")

    return redirect(url_for("common.home"))


@users.get("/onereport/users/reports")
@login_required
def get_all_reports() -> str:
    if not_permitted(current_user.role, misc.Role.USER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

    order = request.args.get("order", default="DESC")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "20")

    try:
        pagination = users_service.get_all_reports(
            current_user.company, order, page, per_page
        )
        return render_template(
            "reports/reports.html", current_company=current_user.company, pagination=pagination, page=page, per_page=per_page
        )
    except BadRequestError as be:
        flash(f"{be}", category="danger")
    except NotFoundError as ne:
        flash(f"{ne}", category="info")

    return redirect(url_for("common.home"))


@users.get("/onereport/users/report/<int:id>")
@login_required
def get_report(id: int) -> str:
    if not_permitted(current_user.role, misc.Role.USER):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        abort(401)

    try:
        report = users_service.get_report(id, current_user.company)
        return render_template("reports/uneditable_report.html", report=report)
    except BadRequestError as be:
        flash(f"{be}", category="danger")
    except NotFoundError as ne:
        flash(f"{ne}", category="danger")

    return redirect(url_for("users.get_all_reports"))
