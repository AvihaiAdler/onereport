from onereport import app, forms, generate_urlstr, has_permission
from onereport.bl import managers_service
from onereport.data import misc
from flask import url_for, redirect, flash, render_template, request
from flask_login import current_user, login_required
from onereport.exceptions import (
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
        personnel = managers_service.register_personnel(form)
        if request.method == "GET":
            return render_template("personnel/personnel_registration.html", form=form)

        flash(
            f"החייל.ת {' '.join((personnel.first_name, personnel.last_name))} נוסף.ה בהצלחה",
            category="success",
        )
        return redirect(url_for("home"))
    except BadRequestError as be:
        flash(f"{be}", category="danger")
    except ForbiddenError as fe:
        flash(f"{fe}", category="info")
    except InternalServerError as ie:
        flash(f"{ie}", category="danger")

    return redirect(url_for(generate_urlstr(current_user.role, "register_personnel")))


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
            f"המשתמש.ת {' '.join((personnel.first_name, personnel.last_name))} נרשמה בהצלחה",
            category="success"
        )
        return redirect(
            url_for(generate_urlstr(current_user.role, "get_all_personnel"), id=id)
        )
    except BadRequestError as be:
        flash(f"{be}", category="danger")
    except NotFoundError as ne:
        flash(f"{ne}", category="danger")
    except ForbiddenError as fe:
        flash(f"{fe}", category="info")
    except InternalServerError as ie:
        flash(f"{ie}", category="danger")

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
        flash(f"{fe}", category="info")
    except InternalServerError as ie:
        flash(f"{ie}", category="danger")

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
        flash(f"{be}", category="danger")
    except NotFoundError as ne:
        flash(f"{ne}", category="info")
    except ForbiddenError as fe:
        flash(f"{fe}", category="info")
    except InternalServerError as ie:
        flash(f"{ie}", category="danger")

    return redirect(url_for(generate_urlstr(current_user.role, "get_all_users")))


# TODO:
# pagination
@app.route("/onereport/managers/users", methods=["GET", "POST"])
@login_required
def m_get_all_users() -> str:
    if not has_permission(current_user.role):
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    order_by = request.args.get("order_by", "COMPANY")
    order = request.args.get("order", "ASC")

    try:
        users = managers_service.get_all_users(order_by, order)
        return render_template("users/users.html", users=users)
    except BadRequestError as be:
        flash(f"{be}", category="danger")
    except NotFoundError as ne:
        flash(f"{ne}", category="info")
    return redirect(url_for("home"))


# TODO:
# pagination
@app.route("/onereport/managers/personnel", methods=["GET", "POST"])
@login_required
def m_get_all_personnel() -> str:
    if not has_permission(current_user.role):
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    order_by = request.args.get("order_by", "LAST_NAME")
    order = request.args.get("order", "ASC")

    form = forms.PersonnelListForm()
    try:
        personnel = managers_service.get_all_personnel(
            form, current_user.company, order_by, order
        )
        if request.method == "GET":
            form.company.data = current_user.company

        return render_template(
            "personnel/personnel_list.html", form=form, personnel=personnel
        )
    except BadRequestError as be:
        flash(f"{be}", category="danger")
    except NotFoundError as ne:
        flash(f"{ne}", category="info")

    return redirect(url_for("home"))


@app.route("/onereport/managers/report", methods=["GET", "POST"])
@login_required
def m_create_report() -> str:
    if not has_permission(current_user.role):
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    order_by = request.args.get("order_by", "LAST_NAME")
    order = request.args.get("order", "ASC")

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
        return redirect(url_for(generate_urlstr(current_user.role, "create_report"), order_by=order_by, order=order))
    except BadRequestError as be:
        flash(f"{be}", category="danger")
    except NotFoundError as ne:
        flash(f"{ne}", category="info")
    except InternalServerError as ie:
        flash(f"{ie}", category="danger")

    return redirect(url_for("home"))


@app.get("/onereport/managers/reports")
@login_required
def m_get_all_reports() -> str:
    if not has_permission(current_user.role):
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    company = request.args.get("company", current_user.company)
    order = request.args.get("order", "DESC")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "20")

    try:
        pagination = managers_service.get_all_reports(company, order, page, per_page)
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
        flash(f"{be}", category="danger")
    except NotFoundError as ne:
        flash(f"{ne}", category="info")
    return redirect(url_for("home"))


@app.get("/onereport/managers/report/<int:id>")
@login_required
def m_get_report(id: int) -> str:
    if not has_permission(current_user.role):
        app.logger.warning(f"unauthorized access by {current_user}")
        return redirect(url_for("home"))

    company = request.args.get("company", current_user.company)

    try:
        report = managers_service.get_report(id, company)
        return render_template("reports/uneditable_report.html", report=report)
    except BadRequestError as be:
        flash(f"{be}", category="danger")
    except NotFoundError as ne:
        flash(f"{ne}", category="info")

    return redirect(url_for(generate_urlstr(current_user.role, "get_all_reports"), company=company))
