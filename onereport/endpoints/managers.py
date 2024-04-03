from onereport import app, forms, generate_urlstr, has_permission
from onereport.bl import managers_service
from onereport.data import misc
from onereport.dto import report_dto
from onereport.dal import report_dal
from flask import url_for, redirect, flash, render_template, request
from flask_login import current_user, login_required
from onereport.exceptions.exceptions import (
    BadRequestError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
)

import datetime


@app.route("/onereport/managers/personnel/register", methods=["GET", "POST"])
@login_required
def m_register_personnel() -> str:
    if not has_permission(current_user.role):
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    form = forms.PersonnelRegistrationFrom()
    try:
        managers_service.register_personnel(form)
        return redirect(url_for("home"))
    except BadRequestError as be:
        flash(str(be), category="danger")
    except ForbiddenError as fe:
        flash(str(fe), category="info")
    except InternalServerError as ie:
        flash(str(ie), category="danger")

    return render_template("personnel/personnel_registration.html", form=form)


@app.route("/onereport/managers/users/<id>/register", methods=["GET", "POST"])
@login_required
def m_register_user(id: str) -> str:
    if not has_permission(current_user.role):
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

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
            f"המשתמש.ת {' '.join((personnel.first_name, personnel.last_name))} נרשמה בהצלחה"
        )
        return redirect(
            url_for(generate_urlstr(current_user.role, "get_all_personnel"), id=id)
        )
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="danger")
    except ForbiddenError as fe:
        flash(str(fe), category="info")
    except InternalServerError as ie:
        flash(str(ie), category="danger")

    return redirect(url_for("home"))


@app.route("/onereport/managers/personnel/<id>/update", methods=["GET", "POST"])
@login_required
def m_update_personnel(id: str) -> str:
    if not has_permission(current_user.role):
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

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
                personnel.company,
                personnel.platoon,
            )
            form.active.data = personnel.active
            return render_template("personnel/personnel.html", form=form)
        flash(f"החייל.ת {id} עודכן בהצלחה", category="success")
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="danger")
    except ForbiddenError as fe:
        flash(str(fe), category="info")
    except InternalServerError as ie:
        flash(str(ie), category="danger")

    return redirect(url_for(generate_urlstr(current_user.role, "get_all_personnel")))


@app.route("/onereport/managers/users/<email>/update", methods=["GET", "POST"])
@login_required
def m_update_user(email: str) -> str:
    if not has_permission(current_user.role):
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    form = forms.UserUpdateForm()
    try:
        user = managers_service.update_user(form, email)
        if request.method == "GET":
            form.id.data = user.id
            form.email.data = user.email
            form.first_name.data, form.last_name.data = user.first_name, user.last_name
            form.company.data, form.platoon.data = user.company, user.platoon
            form.role.data = user.role
            form.active.data = user.active

            return render_template("users/user.html", form=form)
        flash(
            f"המשתמש.ת {' '.join((user.first_name, user.last_name))} עודכן בהצלחה",
            category="success",
        )
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="info")
    except ForbiddenError as fe:
        flash(str(fe), category="info")
    except InternalServerError as ie:
        flash(str(ie), category="danger")

    return redirect(url_for(generate_urlstr(current_user.role, "get_all_users")))


# TODO:
# pagination
@app.route("/onereport/managers/users", methods=["GET", "POST"])
@login_required
def m_get_all_users() -> str:
    if not has_permission(current_user.role):
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    order_by = request.args.get("order_by", default="COMPANY")
    order = request.args.get("order", "ASC")

    try:
        users = managers_service.get_all_users(order_by, order)
        return render_template("users/users.html", users=users)
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="info")
    return redirect(url_for("home"))


# TODO:
# pagination
@app.route("/onereport/managers/personnel", methods=["GET", "POST"])
@login_required
def m_get_all_personnel() -> str:
    if not has_permission(current_user.role):
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    order_by = request.args.get("order_by", default="LAST_NAME")
    order = request.args.get("order", "ASC")

    form = forms.PersonnelListForm()
    try:
        personnel = managers_service.get_all_personnel(
            current_user.company, order_by, order
        )
        if request.method == "GET":
            form.company.data = current_user.company

        render_template("personnel/personnel_list.html", form=form, personnel=personnel)
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="info")

    return redirect(url_for("home"))


@app.route("/onereport/managers/report", methods=["GET", "POST"])
@login_required
def m_create_report() -> str:
    if not has_permission(current_user.role):
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    company = request.args.get("company", current_user.company)
    order_by = request.args.get("order_by", "LAST_NAME")
    order = request.args.get("order", "ASC")

    form = forms.UpdateReportForm()
    try:
        personnel = managers_service.report(form, company, order_by, order)
        if request.method == "GET":
            form.order_by = order_by
            form.order = order
            form.company.data = company
        else:
            flash(f"הדוח ליום {datetime.date.today()} נשלח בהצלחה", category="success")
        return render_template(
            "reports/editable_report.html",
            form=form,
            personnel_presence_list=personnel,
        )
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="info")
    except InternalServerError as ie:
        flash(str(ie), category="danger")

    return redirect(url_for("home"))


@app.get("/onereport/managers/reports")
@login_required
def m_get_all_reports() -> str:
    if not has_permission(current_user.role):
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    company = request.args.get("company", current_user.company)
    order = request.args.get("order", "DESC")

    try:
        reports = managers_service.get_all_reports(company, order)
        return render_template(
            "reports/reports.html",
            reports=reports,
            company=misc.Company,
            current_company=company.value,
        )
    except BadRequestError as be:
        flash(str(be), category="danger")
    except NotFoundError as ne:
        flash(str(ne), category="info")
    return redirect(url_for("home"))


@app.get("/onereport/managers/report/<int:id>")
@login_required
def m_get_report(id: int) -> str:
    if not has_permission(current_user.role):
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    company = request.args.get("company", None)

    if not misc.Company.is_valid(current_user.company):
        app.logger.warning(f"{current_user} 's company is invalid")
        flash(f"{current_user.company} אינה פלוגה בגדוד", category="info")

        return redirect(url_for("home"))

    company = company if misc.Company.is_valid(company) else current_user.company
    report = report_dal.find_report_by_id_and_company(id, misc.Company[company])

    if report is None:
        app.logger.error(
            f"{current_user} tried to get a non existing report with id {id} for company {current_user.company}"
        )
        flash(f"הדוח {id} אינו במסד הנתונים", category="danger")

        return redirect(url_for(generate_urlstr(current_user.role, "get_all_reports")))

    app.logger.debug(f"sends {report} to old_report.html for {current_user}")
    return render_template(
        "reports/old_report.html", report=report_dto.ReportDTO(report)
    )
