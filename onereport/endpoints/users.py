from onereport import app, forms, generate_urlstr
from onereport.data import misc
from onereport.bl import users_service
from onereport.exceptions.exceptions import (
    BadRequestError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
)
from flask import url_for, redirect, flash, render_template, request
from flask_login import current_user, login_required
import datetime


def not_permitted() -> bool:
    if not misc.Role.is_valid(current_user.role):
        return False
    return misc.Role.get_level(current_user.role) > misc.Role.get_level(
        misc.Role.USER.name
    )


@app.route("/onereport/users/personnel", methods=["GET", "POST"])
@login_required
def u_get_all_personnel() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    order_by = request.args.get("order_by", default="ID")
    order = request.args.get("order", default="ASC")

    form = forms.PersonnelListForm()
    try:
        personnel = users_service.get_all_personnel(
            form, current_user.company, order_by, order
        )
        return render_template(
            "personnel/personnel_list.html",
            form=form,
            personnel=personnel,
        )
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="info")
    return redirect(url_for("home"))


@app.route("/onereport/users/personnel/<id>/update", methods=["GET", "POST"])
@login_required
def u_update_personnel(id: str) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    form = forms.PersonnelUpdateForm()
    try:
        personnel, ret = users_service.update_personnel(form, id)
        if request.method == "GET":
            form.id.data = personnel.id
            form.first_name.data, form.last_name.data = (
                personnel.first_name,
                personnel.last_name,
            )
            form.company.data = personnel.company
            form.active.data = personnel.active

            return render_template(
                "personnel/personnel.html",
                form=form,
                personnel=[personnel],
            )

        if ret:
            flash(
                f"החייל.ת {personnel.first_name} {personnel.last_name} עודכן בהצלחה",
                category="success",
            )
        else:
            flash(
                f"הפעולה עבור החייל.ת {personnel.first_name} {personnel.last_name} לא הושלמה",
                category="danger",
            )
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="danger")
    except ForbiddenError as fe:
        flash(str(fe), category="danger")
    return redirect(url_for(generate_urlstr(current_user.role, "get_all_personnel")))


@app.route("/onereport/users/report", methods=["GET", "POST"])
@login_required
def u_create_report() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

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
            )

        flash(f"הדוח ליום {datetime.date.today()} נשלח בהצלחה", category="success")
        return redirect(url_for(generate_urlstr(current_user.role, "create_report")))
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="danger")
    except InternalServerError as ie:
        flash(str(ie), category="danger")

    return redirect(url_for("home"))


@app.get("/onereport/users/reports")
@login_required
def u_get_all_reports() -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    order = request.args.get("order", default="DESC")

    try:
        reports = users_service.get_all_reports(current_user.company, order)
        return render_template("reports/reports.html", reports=reports)
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="info")

    return redirect(url_for("home"))


@app.get("/onereport/users/report/<int:id>")
@login_required
def u_get_report(id: int) -> str:
    if not_permitted():
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    try:
        report = users_service.get_report(id, current_user.company)
        return render_template("reports/old_report.html", report=report)
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="danger")

    return redirect(url_for(generate_urlstr(current_user.role, "get_all_reports")))
