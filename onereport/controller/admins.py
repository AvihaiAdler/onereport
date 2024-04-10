from onereport.controller import forms
from onereport.bl import admins_service
from onereport.dal.order_attr import Order, PersonnelOrderBy, UserOrderBy
from onereport.data import misc
from onereport.controller.util import generate_url, not_permitted
from flask import (
    url_for,
    redirect,
    flash,
    render_template,
    request,
    Blueprint,
    current_app,
)
from flask_login import current_user, login_required
from onereport.exceptions import BadRequestError, InternalServerError, NotFoundError, UnauthorizedError

admins = Blueprint("admins", __name__)


@admins.route("/onereport/admins/personnel/register", methods=["GET", "POST"])
@login_required
def register_personnel() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    return redirect(url_for(generate_url(misc.Role.MANAGER.name, "register_personnel")))


@admins.route("/onereport/admins/users/<id>/register", methods=["GET", "POST"])
@login_required
def register_user(id: str) -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    return redirect(
        url_for(generate_url(misc.Role.MANAGER.name, "register_user"), id=id)
    )


@admins.route("/onereport/admins/personnel/<id>/update", methods=["GET", "POST"])
@login_required
def update_personnel(id: str) -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    return redirect(
        url_for(generate_url(misc.Role.MANAGER.name, "update_personnel"), id=id)
    )


@admins.route("/onereport/admins/users/<email>/update", methods=["GET", "POST"])
@login_required
def update_user(email: str) -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    return redirect(
        url_for(generate_url(misc.Role.MANAGER.name, "update_user"), email=email)
    )


@admins.route("/onereport/admins/users", methods=["GET", "POST"])
@login_required
def get_all_users() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    order_by = request.args.get("order_by", default=UserOrderBy.COMPANY.name)
    order = request.args.get("order", default=Order.ASC.name)

    try:
        users = admins_service.get_all_users(order_by, order)
        return render_template("users/users.html", users=users)
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)
    except NotFoundError as ne:
        return render_template("errors/error.html", error=ne)


@admins.route("/onereport/admins/personnel", methods=["GET", "POST"])
@login_required
def get_all_personnel() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    company = request.args.get("company", default=current_user.company)
    order_by = request.args.get("order_by", default=PersonnelOrderBy.LAST_NAME.name)
    order = request.args.get("order", default=Order.ASC.name)

    form = forms.PersonnelSortForm()
    try:
        personnel = admins_service.get_all_personnel(
            form, company, order_by, order
        )

        return render_template(
            "personnel/personnel_list.html",
            form=form,
            personnel=personnel,
            company=misc.Company
        )
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)


@admins.route("/onereport/admins/report", methods=["GET", "POST"])
@login_required
def create_report() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    order_by = request.args.get("order_by", default=PersonnelOrderBy.LAST_NAME.name)
    order = request.args.get("order", default=Order.ASC.name)
    return redirect(
        url_for(
            generate_url(misc.Role.MANAGER.name, "create_report"),
            order_by=order_by,
            order=order,
        )
    )


@admins.get("/onereport/admins/reports")
@login_required
def get_all_reports() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    company = request.args.get("company", default=current_user.company)
    order = request.args.get("order", default=Order.DESC.name)
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "20")

    return redirect(
        url_for(
            generate_url(misc.Role.MANAGER.name, "get_all_reports"),
            company=company,
            order=order,
            page=page,
            per_page=per_page,
        )
    )


@admins.get("/onereport/admins/report/<int:id>")
@login_required
def get_report(id: int) -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    company = request.args.get("company", current_user.company)

    return redirect(
        url_for(
            generate_url(misc.Role.MANAGER.name, "get_report"),
            id=id,
            company=company,
        )
    )


@admins.get("/onereport/admins/reports/unified")
@login_required
def get_all_unified_reports() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    order = request.args.get("order", Order.DESC.name)
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "20")

    return redirect(
        url_for(
            generate_url(misc.Role.MANAGER.name, "get_all_unified_reports"),
            order=order,
            page=page,
            per_pageg=per_page,
        )
    )


@admins.get("/onereport/admins/report/unified/<date>")
@login_required
def get_unified_report(date: str) -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    order_by = request.args.get("order_by", default=PersonnelOrderBy.LAST_NAME.name)
    order = request.args.get("order", default=Order.ASC.name)

    return redirect(
        url_for(
            generate_url(misc.Role.MANAGER.name, "get_unified_report"),
            date=date,
            order_by=order_by,
            order=order,
        )
    )


@admins.route("/onereport/admins/personnel/upload", methods=["GET", "POST"])
@login_required
def upload_personnel() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    form = forms.UploadPersonnelForm()
    try:
        admins_service.upload_personnel(form)
    except BadRequestError as be:
        return render_template("errors/error.html", error=be)
    except InternalServerError as ie:
        return render_template("errors/error.html", error=ie)

    return render_template("personnel/upload_personnel.html", form=form)


@admins.get("/onereport/admins/report/delete")
@login_required
def delete_all_reports() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    if admins_service.delete_all_reports():
        flash("כל הדוחות נמחקו בהצלחה", category="success")
    else:
        flash("שגיאת שרת", category="danger")
    return redirect(url_for("common.home"))


@admins.get("/onereport/admins/personnel/delete")
@login_required
def delete_all_personnel() -> str:
    if not_permitted(current_user.role, misc.Role.ADMIN):
        current_app.logger.warning(f"unauthorized access by {current_user}")
        return render_template("errors/error.html", error=UnauthorizedError("אין לך הרשאה לדף זה"))

    if admins_service.delete_all_personnel():
        flash("כל הדוחות נמחקו בהצלחה", category="success")
    else:
        flash("שגיאת שרת", category="danger")
    return redirect(url_for("common.home"))
